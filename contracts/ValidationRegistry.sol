// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "@openzeppelin/contracts/access/Ownable.sol";

contract ValidationRegistry is Ownable {
    address public identityRegistry;

    struct ValidationData {
        address validatorAddress;
        uint256 agentId;
        uint8 response;
        bytes32 responseHash;
        string tag;
        uint256 lastUpdate;
    }

    mapping(bytes32 => ValidationData) private _validations;
    mapping(uint256 => bytes32[]) private _agentValidations;
    mapping(address => bytes32[]) private _validatorRequests;

    event ValidationRequest(
        address indexed validatorAddress,
        uint256 indexed agentId,
        string requestURI,
        bytes32 indexed requestHash
    );

    event ValidationResponse(
        address indexed validatorAddress,
        uint256 indexed agentId,
        bytes32 indexed requestHash,
        uint8 response,
        string responseURI,
        bytes32 responseHash,
        string tag
    );

    constructor() Ownable(msg.sender) {}

    function initialize(address identityRegistry_) external onlyOwner {
        require(identityRegistry == address(0), "Already initialized");
        identityRegistry = identityRegistry_;
    }

    function getIdentityRegistry() external view returns (address) {
        return identityRegistry;
    }

    function validationRequest(
        address validatorAddress,
        uint256 agentId,
        string calldata requestURI,
        bytes32 requestHash
    ) external {
        require(validatorAddress != address(0), "Invalid validator");
        require(requestHash != bytes32(0), "Invalid request hash");

        if (_validations[requestHash].validatorAddress == address(0)) {
            _agentValidations[agentId].push(requestHash);
            _validatorRequests[validatorAddress].push(requestHash);
            
            _validations[requestHash] = ValidationData({
                validatorAddress: validatorAddress,
                agentId: agentId,
                response: 0,
                responseHash: bytes32(0),
                tag: "",
                lastUpdate: block.timestamp
            });
        }

        emit ValidationRequest(validatorAddress, agentId, requestURI, requestHash);
    }

    function validationResponse(
        bytes32 requestHash,
        uint8 response,
        string calldata responseURI,
        bytes32 responseHash,
        string calldata tag
    ) external {
        ValidationData storage validation = _validations[requestHash];
        require(validation.validatorAddress == msg.sender, "Not the validator");
        require(response <= 100, "Response must be 0-100");

        validation.response = response;
        validation.responseHash = responseHash;
        validation.tag = tag;
        validation.lastUpdate = block.timestamp;

        emit ValidationResponse(
            msg.sender,
            validation.agentId,
            requestHash,
            response,
            responseURI,
            responseHash,
            tag
        );
    }

    function getValidationStatus(bytes32 requestHash)
        external
        view
        returns (
            address validatorAddress,
            uint256 agentId,
            uint8 response,
            bytes32 responseHash,
            string memory tag,
            uint256 lastUpdate
        )
    {
        ValidationData memory validation = _validations[requestHash];
        return (
            validation.validatorAddress,
            validation.agentId,
            validation.response,
            validation.responseHash,
            validation.tag,
            validation.lastUpdate
        );
    }

    function getSummary(
        uint256 agentId,
        address[] calldata validatorAddresses,
        string calldata tag
    ) external view returns (uint64 count, uint8 averageResponse) {
        bytes32[] memory validations = _agentValidations[agentId];
        uint256 total = 0;
        uint64 validCount = 0;

        for (uint256 i = 0; i < validations.length; i++) {
            ValidationData memory validation = _validations[validations[i]];
            
            if (validatorAddresses.length > 0) {
                bool found = false;
                for (uint256 j = 0; j < validatorAddresses.length; j++) {
                    if (validation.validatorAddress == validatorAddresses[j]) {
                        found = true;
                        break;
                    }
                }
                if (!found) continue;
            }
            
            if (bytes(tag).length > 0 && keccak256(bytes(validation.tag)) != keccak256(bytes(tag))) {
                continue;
            }
            
            total += validation.response;
            validCount++;
        }

        return (validCount, validCount > 0 ? uint8(total / validCount) : 0);
    }

    function getAgentValidations(uint256 agentId) external view returns (bytes32[] memory) {
        return _agentValidations[agentId];
    }

    function getValidatorRequests(address validatorAddress) external view returns (bytes32[] memory) {
        return _validatorRequests[validatorAddress];
    }
}
