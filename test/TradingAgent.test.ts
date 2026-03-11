import { expect } from "chai";
import { ethers } from "hardhat";
import { TradingAgent, IdentityRegistry } from "../typechain-types";

describe("TradingAgent", function () {
  let tradingAgent: TradingAgent;
  let identityRegistry: IdentityRegistry;
  let owner: any;
  let executor: any;

  beforeEach(async function () {
    [owner, executor] = await ethers.getSigners();

    const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
    identityRegistry = await IdentityRegistry.deploy();
    await identityRegistry.waitForDeployment();

    const agentId = await identityRegistry.register();
    await agentId.wait();

    const TradingAgent = await ethers.getContractFactory("TradingAgent");
    tradingAgent = await TradingAgent.deploy(1, await identityRegistry.getAddress());
    await tradingAgent.waitForDeployment();
  });

  it("Should set executor authorization", async function () {
    await tradingAgent.setExecutor(executor.address, true);
    expect(await tradingAgent.authorizedExecutors(executor.address)).to.equal(true);
  });

  it("Should track trade count", async function () {
    const metrics = await tradingAgent.getPerformanceMetrics();
    expect(metrics._tradeCount).to.equal(0);
  });

  it("Should have correct agent ID", async function () {
    expect(await tradingAgent.agentId()).to.equal(1);
  });
});
