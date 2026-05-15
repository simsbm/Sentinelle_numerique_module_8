
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Sentinelle d'intégrité des médias
contract SentinelleIntegrite {
    // Mapping privé : media_id => hash
    mapping(string => bytes32) private mediaHashes;

    // Événement déclenché lors de la certification
    event MediaCertifie(string mediaId, bytes32 hashValue, uint256 timestamp);

    /// @notice Certifie un média avec son hash
    function certifierMedia(string memory mediaId, bytes32 hashValue) public {
        require(mediaHashes[mediaId] == 0x0, "Media deja certifie");
        mediaHashes[mediaId] = hashValue;
        emit MediaCertifie(mediaId, hashValue, block.timestamp);
    }

    /// @notice Vérifie si un média correspond au hash
    function verifierMedia(string memory mediaId, bytes32 hashValue) public view returns (bool) {
        return mediaHashes[mediaId] == hashValue;
    }
}
