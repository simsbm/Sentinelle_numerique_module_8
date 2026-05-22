/* ================================================================
   script.js — Sentinelle Numérique · Dashboard G8
   ----------------------------------------------------------------
   ORGANISATION DE CE FICHIER :
   1. Configuration (URL de l'API)
   2. Gestion des onglets
   3. Gestion de la sélection de fichier
   4. Certification  → POST /api/certifier
   5. Vérification   → POST /api/verifier
   6. Fonctions d'affichage des résultats
   7. Fonctions utilitaires (loader, formatage, etc.)
   8. Mode démo (données simulées si le backend n'est pas prêt)
   9. Drag & Drop
================================================================ */


/* ================================================================
   1. CONFIGURATION
   ----------------------------------------------------------------
   C'est ICI qu'on change l'URL quand le backend est prêt.
   En développement local avec Docker : http://localhost:80/api
   Si l'API Gateway tourne sur un autre port, changer ici.
================================================================ */
const API_BASE = 'http://localhost:80/api';


/* ================================================================
   2. GESTION DES ONGLETS
   ----------------------------------------------------------------
   switchTab('certify') ou switchTab('verify')
   - Active/désactive la classe "active" sur les boutons d'onglet
   - Affiche/cache les panneaux correspondants
================================================================ */
function switchTab(name) {
  // Récupère tous les boutons d'onglet et met à jour leur classe
  const tabs = document.querySelectorAll('.tab');
  tabs[0].classList.toggle('active', name === 'certify');
  tabs[1].classList.toggle('active', name === 'verify');

  // Affiche le bon panneau
  document.getElementById('panel-certify').classList.toggle('active', name === 'certify');
  document.getElementById('panel-verify').classList.toggle('active', name === 'verify');
}


/* ================================================================
   3. GESTION DE LA SÉLECTION DE FICHIER
   ----------------------------------------------------------------
   Appelé par onchange="onFileSelected('certify')" dans le HTML
   Affiche le nom et la taille du fichier sélectionné sous la zone
================================================================ */
function onFileSelected(panel) {
  const input = document.getElementById('file-' + panel);
  const label = document.getElementById('file-' + panel + '-name');

  if (input.files.length > 0) {
    const fichier = input.files[0];
    // Affiche : "→ nom_du_fichier.jpg  (245.3 Ko)"
    label.textContent = '→ ' + fichier.name + '  (' + formatSize(fichier.size) + ')';
    label.style.display = 'block';
  }
}


/* ================================================================
   4. CERTIFICATION
   ----------------------------------------------------------------
   Flux (Séquence 1 du dossier de conception) :
   Utilisateur → Dashboard → POST /api/certifier → Service G8
   Retour attendu : { tx_id, hash, score, timestamp }

   FormData permet d'envoyer un fichier binaire + des données texte
   dans la même requête HTTP (type multipart/form-data)
================================================================ */
async function submitCertify() {

  // --- Validation des entrées ---
  const fileInput  = document.getElementById('file-certify');
  const scoreInput = document.getElementById('score-input');

  if (!fileInput.files.length) {
    alert('Veuillez sélectionner un fichier média.');
    return;
  }

  const score = parseFloat(scoreInput.value);
  if (isNaN(score) || score < 0 || score > 1) {
    alert('Veuillez entrer un score valide entre 0 et 1.\nExemple : 0.87');
    return;
  }

  // --- Préparation de l'interface ---
  setLoading('certify', true);   // affiche le spinner, désactive le bouton
  hideResult('certify');          // cache un éventuel résultat précédent

  // --- Construction de la requête ---
  // FormData encode automatiquement le fichier en multipart
  const formData = new FormData();
  formData.append('fichier', fileInput.files[0]); // le fichier binaire
  formData.append('score', score);                // le score d'analyse

  try {
    // Appel à l'API Gateway → redirigé vers le service-blockchain (G8)
    const reponse = await fetch(API_BASE + '/certifier', {
      method: 'POST',
      body: formData
      // NE PAS mettre Content-Type manuellement avec FormData
      // Le navigateur le gère automatiquement avec le bon "boundary"
    });

    const donnees = await reponse.json();

    if (reponse.ok) {
      // Succès : affiche tx_id, hash, score, timestamp
      afficherCertificationReussie(donnees);
    } else {
      // Erreur métier retournée par le serveur
      afficherCertificationEchec(donnees.message || 'Erreur serveur inconnue.');
    }

  } catch (erreur) {
    // Le backend n'est pas encore disponible → mode démo
    // SUPPRIMER ce bloc catch quand le vrai backend est prêt
    console.warn('[MODE DEMO] Backend non disponible, simulation activée.');
    afficherCertificationReussie(simulerReponseCertification(fileInput.files[0].name, score));

  } finally {
    // finally s'exécute TOUJOURS (succès ou erreur)
    setLoading('certify', false); // cache le spinner, réactive le bouton
  }
}


/* ================================================================
   5. VÉRIFICATION
   ----------------------------------------------------------------
   Flux (Séquence 2 du dossier de conception) :
   Utilisateur → Dashboard → POST /api/verifier → Service G8
   Retour attendu : { valide: true/false, hash, timestamp, tx_id, score }

   Si valide = true  → "Média authentique, certifié le DD/MM/YY"
   Si valide = false → "Alerte : média modifié ou inconnu"
================================================================ */
async function submitVerify() {

  const fileInput = document.getElementById('file-verify');

  if (!fileInput.files.length) {
    alert('Veuillez sélectionner un fichier média à vérifier.');
    return;
  }

  setLoading('verify', true);
  hideResult('verify');

  const formData = new FormData();
  formData.append('fichier', fileInput.files[0]);

  try {
    const reponse = await fetch(API_BASE + '/verifier', {
      method: 'POST',
      body: formData
    });

    const donnees = await reponse.json();

    if (reponse.ok) {
      afficherResultatVerification(donnees);
    } else {
      afficherErreurVerification(donnees.message || 'Erreur serveur inconnue.');
    }

  } catch (erreur) {
    // Mode démo si le backend n'est pas prêt
    console.warn('[MODE DEMO] Backend non disponible, simulation activée.');
    afficherResultatVerification(simulerReponseVerification());

  } finally {
    setLoading('verify', false);
  }
}


/* ================================================================
   6. FONCTIONS D'AFFICHAGE DES RÉSULTATS
================================================================ */

/* -- Certification réussie --
   Affiche les 4 champs de l'objet Certificate du dossier de conception */
function afficherCertificationReussie(donnees) {
  const header = document.getElementById('result-certify-header');
  const body   = document.getElementById('result-certify-body');

  header.className   = 'result-header success';
  header.textContent = '✓  CERTIFICATION RÉUSSIE — TRANSACTION INSCRITE';

  body.innerHTML = `
    ${ligneResultat('Transaction ID',   donnees.tx_id,                          'highlight')}
    ${ligneResultat('Hash SHA-256',     donnees.hash,                           'highlight')}
    <hr class="divider">
    ${ligneResultat('Score d\'analyse', (donnees.score * 100).toFixed(1) + ' %','ok')}
    ${ligneResultat('Horodatage',       formaterDate(donnees.timestamp),        '')}
    ${ligneResultat('Statut',           'CERTIFIÉ — Inscrit dans la blockchain','ok')}
  `;

  document.getElementById('result-certify').classList.add('active');
}

/* -- Certification échouée -- */
function afficherCertificationEchec(message) {
  const header = document.getElementById('result-certify-header');
  const body   = document.getElementById('result-certify-body');

  header.className   = 'result-header error';
  header.textContent = '✕  ÉCHEC DE CERTIFICATION';
  body.innerHTML     = ligneResultat('Erreur', message, 'bad');

  document.getElementById('result-certify').classList.add('active');
}

/* -- Résultat de vérification (authentique ou alerte) -- */
function afficherResultatVerification(donnees) {
  const header = document.getElementById('result-verify-header');
  const body   = document.getElementById('result-verify-body');

  if (donnees.valide) {
    // Le hash recalculé correspond à celui de la blockchain → authentique
    header.className   = 'result-header success';
    header.textContent = '✓  MÉDIA AUTHENTIQUE — INTÉGRITÉ CONFIRMÉE';

    body.innerHTML = `
      ${ligneResultat('Hash SHA-256 recalculé', donnees.hash,                           'highlight')}
      <hr class="divider">
      ${ligneResultat('Certifié le',            formaterDate(donnees.timestamp),        'ok')}
      ${ligneResultat('Score original',         (donnees.score * 100).toFixed(1) + ' %','ok')}
      ${ligneResultat('Transaction ID',         donnees.tx_id,                          '')}
      ${ligneResultat('Statut',                 'AUTHENTIQUE — Hash correspondant trouvé','ok')}
    `;
  } else {
    // Aucune correspondance → le fichier a été modifié ou n'a jamais été certifié
    header.className   = 'result-header error';
    header.textContent = '⚠  ALERTE — MÉDIA MODIFIÉ OU INCONNU';

    body.innerHTML = `
      ${ligneResultat('Hash SHA-256 recalculé', donnees.hash, 'bad')}
      <hr class="divider">
      ${ligneResultat('Statut',       'INCONNU — Aucune correspondance dans la blockchain', 'bad')}
      ${ligneResultat('Signification','Ce fichier n\'a jamais été certifié, ou il a été modifié depuis sa certification.', '')}
    `;
  }

  document.getElementById('result-verify').classList.add('active');
}

/* -- Erreur lors de la vérification -- */
function afficherErreurVerification(message) {
  const header = document.getElementById('result-verify-header');
  const body   = document.getElementById('result-verify-body');

  header.className   = 'result-header error';
  header.textContent = '✕  ERREUR DE VÉRIFICATION';
  body.innerHTML     = ligneResultat('Erreur', message, 'bad');

  document.getElementById('result-verify').classList.add('active');
}


/* ================================================================
   7. FONCTIONS UTILITAIRES
================================================================ */

/* Génère le HTML d'une ligne clé → valeur dans le bloc résultat
   cls : classe CSS ('highlight', 'ok', 'bad', ou '') */
function ligneResultat(cle, valeur, cls) {
  return `
    <div class="result-row">
      <span class="result-key">${cle}</span>
      <span class="result-val ${cls}">${valeur}</span>
    </div>
  `;
}

/* Active/désactive le loader et le bouton pendant un appel API */
function setLoading(panel, actif) {
  document.getElementById('loader-' + panel).classList.toggle('active', actif);
  document.getElementById('btn-' + panel).disabled = actif;
}

/* Cache le bloc résultat */
function hideResult(panel) {
  document.getElementById('result-' + panel).classList.remove('active');
}

/* Formate un timestamp ISO en date lisible en français
   Ex: "2026-05-07T14:32:00Z" → "07/05/2026 14:32:00" */
function formaterDate(timestamp) {
  if (!timestamp) return 'N/A';
  try {
    return new Date(timestamp).toLocaleString('fr-FR');
  } catch {
    return timestamp; // retourne la valeur brute si la conversion échoue
  }
}

/* Formate une taille en octets en Ko ou Mo lisible
   Ex: 245300 → "245.3 Ko" */
function formatSize(octets) {
  if (octets < 1024)     return octets + ' B';
  if (octets < 1048576)  return (octets / 1024).toFixed(1) + ' Ko';
  return (octets / 1048576).toFixed(1) + ' Mo';
}


/* ================================================================
   8. MODE DÉMO — Données simulées
   ----------------------------------------------------------------
   Ces fonctions simulent ce que le vrai backend retournerait.
   Elles sont appelées dans le bloc catch quand l'API n'est pas joignable.

   ⚠ SUPPRIMER ou COMMENTER ces fonctions en production
      (quand le vrai backend sera connecté)
================================================================ */

/* Simule une réponse de certification réussie */
function simulerReponseCertification(nomFichier, score) {
  return {
    tx_id:     '0x' + hexAleatoire(64),   // faux identifiant de transaction
    hash:      hexAleatoire(64),           // faux hash SHA-256
    score:     score,
    timestamp: new Date().toISOString()
  };
}

/* Simule une réponse de vérification (60% de chance d'être "valide") */
function simulerReponseVerification() {
  const valide = Math.random() > 0.4;
  return {
    valide,
    hash:      hexAleatoire(64),
    tx_id:     valide ? '0x' + hexAleatoire(64) : null,
    score:     valide ? parseFloat(Math.random().toFixed(2)) : null,
    timestamp: valide ? new Date(Date.now() - 86400000).toISOString() : null
  };
}

/* Génère une chaîne hexadécimale aléatoire de longueur donnée */
function hexAleatoire(longueur) {
  return Array.from(
    { length: longueur },
    () => Math.floor(Math.random() * 16).toString(16)
  ).join('');
}


/* ================================================================
   9. DRAG & DROP
   ----------------------------------------------------------------
   Permet de glisser-déposer un fichier directement sur la zone d'upload.
   dragover  → empêche le comportement par défaut (ouvrir le fichier)
               et ajoute un style visuel
   dragleave → retire le style visuel
   drop      → récupère le fichier déposé et simule une sélection
================================================================ */
['certify', 'verify'].forEach(function(panel) {
  const zone = document.getElementById('drop-' + panel);

  zone.addEventListener('dragover', function(e) {
    e.preventDefault(); // OBLIGATOIRE sinon le drop ne fonctionne pas
    zone.classList.add('drag-over'); // style visuel défini dans le CSS
  });

  zone.addEventListener('dragleave', function() {
    zone.classList.remove('drag-over');
  });

  zone.addEventListener('drop', function(e) {
    e.preventDefault();
    zone.classList.remove('drag-over');

    // Transfère les fichiers déposés vers l'input file
    const input = document.getElementById('file-' + panel);
    input.files = e.dataTransfer.files;

    // Déclenche l'affichage du nom de fichier comme si l'utilisateur avait cliqué
    onFileSelected(panel);
  });
});
