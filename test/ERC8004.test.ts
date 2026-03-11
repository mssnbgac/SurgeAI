import { expect } from "chai";
import { ethers } from "hardhat";
import { IdentityRegistry, ReputationRegistry, ValidationRegistry } from "../typechain-types";

describe("ERC-8004 Registries", function () {
  let identityRegistry: IdentityRegistry;
  let reputationRegistry: ReputationRegistry;
  let validationRegistry: ValidationRegistry;
  let owner: any;
  let client: any;

  beforeEach(async function () {
    [owner, client] = await ethers.getSigners();

    const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
    identityRegistry = await IdentityRegistry.deploy();
    await identityRegistry.waitForDeployment();

    const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
    reputationRegistry = await ReputationRegistry.deploy();
    await reputationRegistry.waitForDeployment();
    await reputationRegistry.initialize(await identityRegistry.getAddress());

    const ValidationRegistry = await ethers.getContractFactory("ValidationRegistry");
    validationRegistry = await ValidationRegistry.deploy();
    await validationRegistry.waitForDeployment();
    await validationRegistry.initialize(await identityRegistry.getAddress());
  });

  describe("IdentityRegistry", function () {
    it("Should register a new agent", async function () {
      const tx = await identityRegistry["register(string)"]("ipfs://test");
      const receipt = await tx.wait();
      
      expect(receipt).to.not.be.null;
    });

    it("Should set agent URI", async function () {
      await identityRegistry["register()"]();
      await identityRegistry.setAgentURI(1, "ipfs://updated");
      
      const uri = await identityRegistry.tokenURI(1);
      expect(uri).to.equal("ipfs://updated");
    });
  });

  describe("ReputationRegistry", function () {
    beforeEach(async function () {
      await identityRegistry["register()"]();
    });

    it("Should give feedback", async function () {
      await reputationRegistry.connect(client).giveFeedback(
        1, // agentId
        85, // value
        0, // decimals
        "quality",
        "",
        "",
        "",
        ethers.ZeroHash
      );

      const lastIndex = await reputationRegistry.getLastIndex(1, client.address);
      expect(lastIndex).to.equal(1);
    });

    it("Should calculate summary", async function () {
      await reputationRegistry.connect(client).giveFeedback(1, 90, 0, "", "", "", "", ethers.ZeroHash);
      
      const summary = await reputationRegistry.getSummary(1, [client.address], "", "");
      expect(summary.count).to.equal(1);
      expect(summary.summaryValue).to.equal(90);
    });
  });

  describe("ValidationRegistry", function () {
    beforeEach(async function () {
      await identityRegistry["register()"]();
    });

    it("Should request validation", async function () {
      const requestHash = ethers.keccak256(ethers.toUtf8Bytes("test-request"));
      
      await validationRegistry.validationRequest(
        client.address,
        1,
        "ipfs://request",
        requestHash
      );

      const validations = await validationRegistry.getAgentValidations(1);
      expect(validations.length).to.equal(1);
    });

    it("Should respond to validation", async function () {
      const requestHash = ethers.keccak256(ethers.toUtf8Bytes("test-request"));
      
      await validationRegistry.validationRequest(client.address, 1, "ipfs://request", requestHash);
      await validationRegistry.connect(client).validationResponse(requestHash, 100, "", ethers.ZeroHash, "passed");

      const status = await validationRegistry.getValidationStatus(requestHash);
      expect(status.response).to.equal(100);
    });
  });
});
