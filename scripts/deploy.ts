import { ethers } from "hardhat";

async function main() {
  console.log("Deploying ERC-8004 Trading Agent...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await ethers.provider.getBalance(deployer.address)).toString());

  // Deploy Identity Registry
  console.log("\n1. Deploying IdentityRegistry...");
  const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
  const identityRegistry = await IdentityRegistry.deploy();
  await identityRegistry.waitForDeployment();
  const identityAddress = await identityRegistry.getAddress();
  console.log("IdentityRegistry deployed to:", identityAddress);

  // Deploy Reputation Registry
  console.log("\n2. Deploying ReputationRegistry...");
  const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
  const reputationRegistry = await ReputationRegistry.deploy();
  await reputationRegistry.waitForDeployment();
  const reputationAddress = await reputationRegistry.getAddress();
  console.log("ReputationRegistry deployed to:", reputationAddress);

  // Initialize Reputation Registry
  await reputationRegistry.initialize(identityAddress);
  console.log("ReputationRegistry initialized");

  // Deploy Validation Registry
  console.log("\n3. Deploying ValidationRegistry...");
  const ValidationRegistry = await ethers.getContractFactory("ValidationRegistry");
  const validationRegistry = await ValidationRegistry.deploy();
  await validationRegistry.waitForDeployment();
  const validationAddress = await validationRegistry.getAddress();
  console.log("ValidationRegistry deployed to:", validationAddress);

  // Initialize Validation Registry
  await validationRegistry.initialize(identityAddress);
  console.log("ValidationRegistry initialized");

  // Register Agent
  console.log("\n4. Registering Agent...");
  const agentURI = "ipfs://QmExample"; // Replace with actual IPFS URI
  const registerTx = await identityRegistry["register(string)"](agentURI);
  const receipt = await registerTx.wait();
  
  const agentId = 1; // First agent
  console.log("Agent registered with ID:", agentId);

  // Deploy Trading Agent
  console.log("\n5. Deploying TradingAgent...");
  const TradingAgent = await ethers.getContractFactory("TradingAgent");
  const tradingAgent = await TradingAgent.deploy(agentId, identityAddress);
  await tradingAgent.waitForDeployment();
  const tradingAddress = await tradingAgent.getAddress();
  console.log("TradingAgent deployed to:", tradingAddress);

  // Summary
  console.log("\n=== Deployment Summary ===");
  console.log("IdentityRegistry:", identityAddress);
  console.log("ReputationRegistry:", reputationAddress);
  console.log("ValidationRegistry:", validationAddress);
  console.log("TradingAgent:", tradingAddress);
  console.log("Agent ID:", agentId);
  console.log("\nSave these addresses to your .env file!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
