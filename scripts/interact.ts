import { ethers } from "hardhat";

async function main() {
  console.log("Interacting with deployed contracts...\n");

  // Load contract addresses from environment
  const IDENTITY_REGISTRY = process.env.IDENTITY_REGISTRY_ADDRESS || "";
  const REPUTATION_REGISTRY = process.env.REPUTATION_REGISTRY_ADDRESS || "";
  const TRADING_AGENT = process.env.TRADING_AGENT_ADDRESS || "";
  const AGENT_ID = process.env.AGENT_ID || "1";

  if (!IDENTITY_REGISTRY || !REPUTATION_REGISTRY || !TRADING_AGENT) {
    console.error("Please set contract addresses in .env file");
    process.exit(1);
  }

  const [signer] = await ethers.getSigners();
  console.log("Using account:", signer.address);

  // Get contract instances
  const identityRegistry = await ethers.getContractAt("IdentityRegistry", IDENTITY_REGISTRY);
  const reputationRegistry = await ethers.getContractAt("ReputationRegistry", REPUTATION_REGISTRY);
  const tradingAgent = await ethers.getContractAt("TradingAgent", TRADING_AGENT);

  // Check agent info
  console.log("\n=== Agent Information ===");
  const agentURI = await identityRegistry.tokenURI(AGENT_ID);
  console.log("Agent URI:", agentURI);
  
  const agentWallet = await identityRegistry.getAgentWallet(AGENT_ID);
  console.log("Agent Wallet:", agentWallet);

  // Check reputation
  console.log("\n=== Reputation ===");
  const clients = await reputationRegistry.getClients(AGENT_ID);
  console.log("Number of clients:", clients.length);

  if (clients.length > 0) {
    const summary = await reputationRegistry.getSummary(AGENT_ID, clients, "", "");
    console.log("Feedback count:", summary.count.toString());
    console.log("Average score:", summary.summaryValue.toString());
  }

  // Check trading stats
  console.log("\n=== Trading Performance ===");
  const metrics = await tradingAgent.getPerformanceMetrics();
  console.log("Total trades:", metrics._tradeCount.toString());
  console.log("Total profit:", ethers.formatEther(metrics._totalProfit));
  console.log("Total loss:", ethers.formatEther(metrics._totalLoss));

  // Example: Give feedback (uncomment to use)
  // console.log("\n=== Giving Feedback ===");
  // const tx = await reputationRegistry.giveFeedback(
  //   AGENT_ID,
  //   95, // score
  //   0,  // decimals
  //   "quality",
  //   "",
  //   "",
  //   "",
  //   ethers.ZeroHash
  // );
  // await tx.wait();
  // console.log("Feedback submitted!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
