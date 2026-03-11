// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

contract IdentityRegistry is ERC721URIStorage, Ownable, EIP712 {
    using ECDSA for bytes32;

    uint256 private _nextAgentId;
    
    mapping(uint256 => mapping(string => bytes)) private _metadata;
    mapping(uint256 => address) private _agentWallets;

    bytes32 private constant SET_WALLET_TYPEHASH = 
        keccak256("SetAgentWallet(uint256 agentId,address newWallet,uint256 deadline)");

    event Registered(uint256 indexed agentId, string agentURI, address indexed owner);
    event URIUpdated(uint256 indexed agentId, string newURI, address indexed updatedBy);
    event MetadataSet(uint256 indexed agentId, string indexed indexedMetadataKey, string metadataKey, bytes metadataValue);
    event AgentWalletSet(uint256 indexed agentId, address indexed newWallet);

    constructor() ERC721("ERC8004 Agent", "AGENT") EIP712("IdentityRegistry", "1") Ownable(msg.sender) {
        _nextAgentId = 1;
    }

    function register() external returns (uint256) {
        return _register(msg.sender, "");
    }

    function register(string calldata agentURI) external returns (uint256) {
        return _register(msg.sender, agentURI);
    }

    function _register(address owner, string memory agentURI) private returns (uint256) {
        uint256 agentId = _nextAgentId++;
        _safeMint(owner, agentId);
        
        if (bytes(agentURI).length > 0) {
            _setTokenURI(agentId, agentURI);
        }

        _agentWallets[agentId] = owner;
        emit MetadataSet(agentId, "agentWallet", "agentWallet", abi.encode(owner));
        emit Registered(agentId, agentURI, owner);
        
        return agentId;
    }

    function setAgentURI(uint256 agentId, string calldata newURI) external {
        require(ownerOf(agentId) == msg.sender, "Not agent owner");
        _setTokenURI(agentId, newURI);
        emit URIUpdated(agentId, newURI, msg.sender);
    }

    function getMetadata(uint256 agentId, string memory metadataKey) external view returns (bytes memory) {
        require(ownerOf(agentId) != address(0), "Agent does not exist");
        return _metadata[agentId][metadataKey];
    }

    function setMetadata(uint256 agentId, string memory metadataKey, bytes memory metadataValue) external {
        require(ownerOf(agentId) == msg.sender, "Not agent owner");
        require(keccak256(bytes(metadataKey)) != keccak256(bytes("agentWallet")), "Use setAgentWallet");
        
        _metadata[agentId][metadataKey] = metadataValue;
        emit MetadataSet(agentId, metadataKey, metadataKey, metadataValue);
    }

    function setAgentWallet(
        uint256 agentId,
        address newWallet,
        uint256 deadline,
        bytes calldata signature
    ) external {
        require(ownerOf(agentId) == msg.sender, "Not agent owner");
        require(block.timestamp <= deadline, "Signature expired");
        
        bytes32 structHash = keccak256(abi.encode(SET_WALLET_TYPEHASH, agentId, newWallet, deadline));
        bytes32 hash = _hashTypedDataV4(structHash);
        address signer = hash.recover(signature);
        
        require(signer == newWallet, "Invalid signature");
        
        _agentWallets[agentId] = newWallet;
        _metadata[agentId]["agentWallet"] = abi.encode(newWallet);
        emit MetadataSet(agentId, "agentWallet", "agentWallet", abi.encode(newWallet));
        emit AgentWalletSet(agentId, newWallet);
    }

    function getAgentWallet(uint256 agentId) external view returns (address) {
        return _agentWallets[agentId];
    }

    function unsetAgentWallet(uint256 agentId) external {
        require(ownerOf(agentId) == msg.sender, "Not agent owner");
        _agentWallets[agentId] = address(0);
        _metadata[agentId]["agentWallet"] = "";
        emit MetadataSet(agentId, "agentWallet", "agentWallet", "");
    }

    function _update(address to, uint256 tokenId, address auth) internal virtual override returns (address) {
        address previousOwner = super._update(to, tokenId, auth);
        
        if (previousOwner != address(0) && to != address(0)) {
            _agentWallets[tokenId] = address(0);
            _metadata[tokenId]["agentWallet"] = "";
        }
        
        return previousOwner;
    }
}
