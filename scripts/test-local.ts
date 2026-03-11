import { ethers } from "hardhat";
import * as dotenv from "dotenv";

dotenv.config();

async function main() {
  console.log("Testing Deployed Contracts...\n");

  const [owner, client] = await ethers.getSigners();
  
  // Get contract instances
  const identityRegistry = await ethers.getContractAt(
    "IdentityRegistry",
    process.env.IDENTITY_REGISTRY_ADDRESS!
  );
  
  const reputationRegistry = await ethers.getContractAt(
    "ReputationRegistry",
    process.env.REPUTATION_REGISTRY_ADDRESS!
  );
  
  const validationRegistry = await ethers.getContractAt(
    "ValidationRegistry",
    process.env.VALIDATION_REGISTRY_ADDRESS!
  );
  
  const tradingAgent = await ethers.getContractAt(
    "TradingAgent",
    process.env.TRADING_AGENT_ADDRESS!
  );

  console.log("=== Testing Identity Registry ===");
  const agentURI = await identityRegistry.tokenURI(1);
  console.log("Agent URI:", agentURI);
  
  const agentOwner = await identityRegistry.ownerOf(1);
  console.log("Agent Owner:", agentOwner);
  console.log("✅ Identity Registry working!\n");

  console.log("=== Testing Reputation Registry ===");
  console.log("Giving feedback from client...");
  await reputationRegistry.connect(client).giveFeedback(
    1, // agentId
    95, // value (95/100)
    0, // decimals
    "quality",
    "excellent",
    "https://agent.example.com",
    "ipfs://feedback-data",
    ethers.ZeroHash
  );
  
  const lastIndex = await reputationRegistry.getLastIndex(1, client.address);
  console.log("Feedback submitted, index:", lastIndex.toString());
  
  const summary = await reputationRegistry.getSummary(1, [client.address], "", "");
  console.log("Reputation Summary:");
  console.log("  - Count:", summary.count.toString());
  console.log("  - Average Score:", summary.summaryValue.toString());
  console.log("✅ Reputation Registry working!\n");

  console.log("=== Testing Validation Registry ===");
  const requestHash = ethers.keccak256(ethers.toUtf8Bytes("test-validation-request"));
  
  console.log("Requesting validation...");
  await validationRegistry.validationRequest(
    client.address, // validator
    1, // agentId
    "ipfs://validation-request",
    requestHash
  );
  
  console.log("Validator responding...");
  await validationRegistry.connect(client).validationResponse(
    requestHash,
    100, // response (100 = passed)
    "ipfs://validation-proof",
    ethers.ZeroHash,
    "verified"
  );
  
  const status = await validationRegistry.getValidationStatus(requestHash);
  console.log("Validation Status:");
  console.log("  - Validator:", status.validatorAddress);
  console.log("  - Response:", status.response.toString());
  console.log("  - Tag:", status.tag);
  console.log("✅ Validation Registry working!\n");

  console.log("=== Testing Trading Agent ===");
  const agentId = await tradingAgent.agentId();
  console.log("Trading Agent ID:", agentId.toString());
  
  const tradeCount = await tradingAgent.tradeCount();
  console.log("Trade Count:", tradeCount.toString());
  
  const isAuthorized = await tradingAgent.authorizedExecutors(owner.address);
  console.log("Owner Authorized:", isAuthorized);
  console.log("✅ Trading Agent working!\n");

  console.log("=== All Tests Passed! ===");
  console.log("\n🎉 Your ERC-8004 Trading Agent is fully functional!");
  console.log("\nNext steps:");
  console.log("1. Start the Python AI agent: cd agent && python main.py");
  console.log("2. Start the backend API: cd backend && npm run dev");
  console.log("3. Start the frontend: cd frontend && npm run dev");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
