import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("\n" + "=".repeat(60));
  console.log("🚀 DEPLOYING TO BASE SEPOLIA TESTNET");
  console.log("=".repeat(60) + "\n");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "ETH");
  
  if (balance === 0n) {
    console.log("\n❌ ERROR: No ETH balance!");
    console.log("Get testnet ETH from: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet");
    process.exit(1);
  }

  const network = await ethers.provider.getNetwork();
  console.log("Network:", network.name, "Chain ID:", network.chainId.toString());
  console.log();

  // Deploy Identity Registry
  console.log("1️⃣  Deploying IdentityRegistry...");
  const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
  const identityRegistry = await IdentityRegistry.deploy();
  await identityRegistry.waitForDeployment();
  const identityAddress = await identityRegistry.getAddress();
  console.log("✅ IdentityRegistry:", identityAddress);

  // Deploy Reputation Registry
  console.log("\n2️⃣  Deploying ReputationRegistry...");
  const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
  const reputationRegistry = await ReputationRegistry.deploy();
  await reputationRegistry.waitForDeployment();
  const reputationAddress = await reputationRegistry.getAddress();
  console.log("✅ ReputationRegistry:", reputationAddress);

  // Initialize Reputation Registry
  console.log("   Initializing...");
  await reputationRegistry.initialize(identityAddress);
  console.log("   ✅ Initialized");

  // Deploy Validation Registry
  console.log("\n3️⃣  Deploying ValidationRegistry...");
  const ValidationRegistry = await ethers.getContractFactory("ValidationRegistry");
  const validationRegistry = await ValidationRegistry.deploy();
  await validationRegistry.waitForDeployment();
  const validationAddress = await validationRegistry.getAddress();
  console.log("✅ ValidationRegistry:", validationAddress);

  // Initialize Validation Registry
  console.log("   Initializing...");
  await validationRegistry.initialize(identityAddress);
  console.log("   ✅ Initialized");

  // Register Agent
  console.log("\n4️⃣  Registering Agent...");
  
  // Read agent registration file
  const registrationPath = path.join(__dirname, "../agent/registration.json");
  let agentURI = "ipfs://QmExample";
  
  if (fs.existsSync(registrationPath)) {
    console.log("   Found registration.json, uploading to IPFS...");
    // In production, upload to IPFS here
    // For now, use placeholder
    agentURI = "ipfs://QmExampleAgentRegistration";
  }
  
  const registerTx = await identityRegistry["register(string)"](agentURI);
  await registerTx.wait();
  console.log("✅ Agent registered with ID: 1");
  console.log("   URI:", agentURI);

  // Deploy Trading Agent
  console.log("\n5️⃣  Deploying TradingAgent...");
  const TradingAgent = await ethers.getContractFactory("TradingAgent");
  const tradingAgent = await TradingAgent.deploy(1, identityAddress);
  await tradingAgent.waitForDeployment();
  const tradingAddress = await tradingAgent.getAddress();
  console.log("✅ TradingAgent:", tradingAddress);

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId.toString(),
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      IdentityRegistry: identityAddress,
      ReputationRegistry: reputationAddress,
      ValidationRegistry: validationAddress,
      TradingAgent: tradingAddress
    },
    agentId: 1,
    agentURI: agentURI
  };

  const deploymentPath = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentPath)) {
    fs.mkdirSync(deploymentPath, { recursive: true });
  }

  const filename = `deployment-${network.chainId}-${Date.now()}.json`;
  fs.writeFileSync(
    path.join(deploymentPath, filename),
    JSON.stringify(deploymentInfo, null, 2)
  );

  // Print summary
  console.log("\n" + "=".repeat(60));
  console.log("🎉 DEPLOYMENT COMPLETE!");
  console.log("=".repeat(60));
  console.log("\n📋 Contract Addresses:");
  console.log("   IdentityRegistry:    ", identityAddress);
  console.log("   ReputationRegistry:  ", reputationAddress);
  console.log("   ValidationRegistry:  ", validationAddress);
  console.log("   TradingAgent:        ", tradingAddress);
  console.log("\n🔍 Verify on Basescan:");
  console.log("   https://sepolia.basescan.org/address/" + identityAddress);
  console.log("\n💾 Deployment saved to:");
  console.log("   deployments/" + filename);
  console.log("\n📝 Next Steps:");
  console.log("   1. Update .env with these addresses");
  console.log("   2. Verify contracts: npm run verify");
  console.log("   3. Run agent: cd agent && python main_production.py");
  console.log("   4. Start dashboard: cd frontend && npm run dev");
  console.log("\n" + "=".repeat(60) + "\n");

  // Create .env update instructions
  console.log("📄 Add to your .env file:");
  console.log("─".repeat(60));
  console.log(`IDENTITY_REGISTRY_ADDRESS=${identityAddress}`);
  console.log(`REPUTATION_REGISTRY_ADDRESS=${reputationAddress}`);
  console.log(`VALIDATION_REGISTRY_ADDRESS=${validationAddress}`);
  console.log(`TRADING_AGENT_ADDRESS=${tradingAddress}`);
  console.log(`AGENT_ID=1`);
  console.log("─".repeat(60) + "\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });
