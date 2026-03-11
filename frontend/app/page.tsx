"use client";

import { useState, useEffect } from "react";
import { ethers } from "ethers";

// Extend Window interface to include ethereum
declare global {
  interface Window {
    ethereum?: any;
  }
}

// Contract ABIs (minimal)
const IDENTITY_REGISTRY_ABI = [
  "function tokenURI(uint256 tokenId) view returns (string)",
  "function ownerOf(uint256 tokenId) view returns (address)"
];

const REPUTATION_REGISTRY_ABI = [
  "function getSummary(uint256 agentId, address[] clientAddresses, string tag1, string tag2) view returns (uint64 count, int128 summaryValue, uint8 summaryValueDecimals)",
  "function getClients(uint256 agentId) view returns (address[])",
  "function giveFeedback(uint256 agentId, int128 value, uint8 valueDecimals, string tag1, string tag2, string endpoint, string feedbackURI, bytes32 feedbackHash) external"
];

const TRADING_AGENT_ABI = [
  "function tradeCount() view returns (uint256)",
  "function getPerformanceMetrics() view returns (uint256 _tradeCount, uint256 _totalProfit, uint256 _totalLoss)"
];

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalTrades: 0,
    totalProfit: 0,
    winRate: 0,
    activePositions: 0
  });
  
  const [agentStatus, setAgentStatus] = useState({
    agentId: 1,
    status: "Loading...",
    reputationScore: 0,
    validations: 0
  });
  
  const [wallet, setWallet] = useState<{
    address: string;
    connected: boolean;
    chainId: number | null;
  }>({
    address: "",
    connected: false,
    chainId: null
  });
  
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackValue, setFeedbackValue] = useState(95);
  const [submitting, setSubmitting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function connectWallet() {
    try {
      // Check if MetaMask is installed
      if (typeof window === 'undefined') {
        alert('Please open this in a browser!');
        return;
      }

      if (typeof window.ethereum === 'undefined') {
        const install = confirm(
          '🦊 MetaMask is not installed!\n\n' +
          'MetaMask is required to connect your wallet and submit feedback.\n\n' +
          'Click OK to visit MetaMask website, or Cancel to continue viewing the dashboard.'
        );
        if (install) {
          window.open('https://metamask.io/download/', '_blank');
        }
        return;
      }

      // Request account access
      const provider = new ethers.BrowserProvider(window.ethereum);
      const accounts = await provider.send("eth_requestAccounts", []);
      
      if (accounts.length === 0) {
        alert('No accounts found. Please create an account in MetaMask.');
        return;
      }

      const network = await provider.getNetwork();
      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      // Check if on correct network
      if (Number(network.chainId) !== 1337 && Number(network.chainId) !== 31337) {
        const switchNetwork = confirm(
          `⚠️ Wrong Network!\n\n` +
          `You're on Chain ID: ${network.chainId}\n` +
          `Expected: 1337 (Hardhat Local)\n\n` +
          `Click OK to see instructions for adding the local network.`
        );
        
        if (switchNetwork) {
          alert(
            '📝 Add Hardhat Local Network to MetaMask:\n\n' +
            '1. Open MetaMask\n' +
            '2. Click network dropdown\n' +
            '3. Click "Add Network" → "Add network manually"\n' +
            '4. Enter these details:\n' +
            '   • Network Name: Hardhat Local\n' +
            '   • RPC URL: http://localhost:8545\n' +
            '   • Chain ID: 1337\n' +
            '   • Currency: ETH\n' +
            '5. Click Save\n' +
            '6. Switch to Hardhat Local network\n' +
            '7. Click "Connect Wallet" again'
          );
        }
        return;
      }

      setWallet({
        address,
        connected: true,
        chainId: Number(network.chainId)
      });

      console.log('✅ Wallet connected:', address);
      console.log('✅ Network:', network.chainId);

      // Listen for account changes
      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length === 0) {
          setWallet({ address: "", connected: false, chainId: null });
          console.log('Wallet disconnected');
        } else {
          setWallet(prev => ({ ...prev, address: accounts[0] }));
          console.log('Account changed:', accounts[0]);
        }
      });

      // Listen for chain changes
      window.ethereum.on('chainChanged', (chainId: string) => {
        console.log('Network changed:', chainId);
        window.location.reload();
      });

    } catch (err: any) {
      console.error("Error connecting wallet:", err);
      
      if (err.code === 4001) {
        alert('❌ Connection rejected. Please approve the connection in MetaMask.');
      } else if (err.code === -32002) {
        alert('⏳ Connection request pending. Please check MetaMask.');
      } else {
        alert(`❌ Failed to connect wallet:\n\n${err.message}`);
      }
    }
  }

  async function disconnectWallet() {
    setWallet({ address: "", connected: false, chainId: null });
  }

  async function submitFeedback() {
    if (!wallet.connected) {
      alert("⚠️ Please connect your wallet first!\n\nClick the 'Connect Wallet' button in the top right.");
      return;
    }

    setSubmitting(true);
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      
      const reputationAddress = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512";
      const reputationRegistry = new ethers.Contract(
        reputationAddress,
        REPUTATION_REGISTRY_ABI,
        signer
      );

      console.log('Submitting feedback:', {
        agentId: 1,
        value: feedbackValue,
        from: wallet.address
      });

      const tx = await reputationRegistry.giveFeedback(
        1, // agentId
        feedbackValue,
        0, // decimals
        "quality",
        "user-feedback",
        "",
        "",
        ethers.ZeroHash
      );

      console.log('Transaction sent:', tx.hash);
      alert('⏳ Transaction submitted! Waiting for confirmation...');

      const receipt = await tx.wait();
      console.log('Transaction confirmed:', receipt);
      
      alert('✅ Feedback submitted successfully!\n\nTransaction: ' + tx.hash.slice(0, 10) + '...');
      
      // Refresh data to show new feedback
      await loadData();
      
    } catch (err: any) {
      console.error("Error submitting feedback:", err);
      
      if (err.code === 4001) {
        alert('❌ Transaction rejected in MetaMask.');
      } else if (err.code === 'ACTION_REJECTED') {
        alert('❌ Transaction rejected.');
      } else {
        alert(`❌ Failed to submit feedback:\n\n${err.message || err.reason || 'Unknown error'}`);
      }
    } finally {
      setSubmitting(false);
    }
  }

  async function testWithoutWallet() {
    // Demo mode - simulate wallet connection for testing
    const demoAddress = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";
    setWallet({
      address: demoAddress,
      connected: true,
      chainId: 1337
    });
    alert('🎭 Demo Mode Activated!\n\nUsing test address: ' + demoAddress + '\n\nNote: You cannot submit real transactions in demo mode.');
  }

  async function loadData() {
    setRefreshing(true);
    try {
      const provider = new ethers.JsonRpcProvider("http://localhost:8545");
      await provider.getNetwork();
      setIsConnected(true);
      setError(null);

      const identityAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
      const reputationAddress = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512";
      const tradingAgentAddress = "0x0165878A594ca255338adfa4d48449f69242Eb8F";

      const identityRegistry = new ethers.Contract(identityAddress, IDENTITY_REGISTRY_ABI, provider);
      const reputationRegistry = new ethers.Contract(reputationAddress, REPUTATION_REGISTRY_ABI, provider);
      const tradingAgent = new ethers.Contract(tradingAgentAddress, TRADING_AGENT_ABI, provider);

      try {
        await identityRegistry.ownerOf(1);
        setAgentStatus(prev => ({ ...prev, status: "Active", agentId: 1 }));
      } catch (e) {
        setAgentStatus(prev => ({ ...prev, status: "Inactive" }));
      }

      try {
        const clients = await reputationRegistry.getClients(1);
        if (clients.length > 0) {
          const summary = await reputationRegistry.getSummary(1, clients, "", "");
          setAgentStatus(prev => ({
            ...prev,
            reputationScore: Number(summary.summaryValue),
            validations: Number(summary.count)
          }));
        }
      } catch (e) {
        console.log("No reputation data yet");
      }

      try {
        const metrics = await tradingAgent.getPerformanceMetrics();
        const tradeCount = Number(metrics._tradeCount);
        const totalProfit = Number(metrics._totalProfit);
        const totalLoss = Number(metrics._totalLoss);
        const winRate = tradeCount > 0 ? ((tradeCount - totalLoss) / tradeCount) * 100 : 0;
        
        setStats({
          totalTrades: tradeCount,
          totalProfit: totalProfit - totalLoss,
          winRate: winRate,
          activePositions: 0
        });
      } catch (e) {
        console.log("No trading data yet");
      }

      setLastRefresh(new Date());

    } catch (err: any) {
      console.error("Error loading data:", err);
      setError(err.message);
      setIsConnected(false);
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold mb-2">AI Trading Agent Dashboard</h1>
            <p className="text-gray-400">ERC-8004 Multi-Strategy Agent</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm">{isConnected ? 'Node Connected' : 'Node Disconnected'}</span>
            </div>
            {wallet.connected ? (
              <div className="flex items-center gap-2">
                <div className="bg-gray-800 px-4 py-2 rounded-lg">
                  <p className="text-xs text-gray-400">Connected</p>
                  <p className="text-sm font-mono">{wallet.address.slice(0, 6)}...{wallet.address.slice(-4)}</p>
                  {wallet.chainId && (
                    <p className="text-xs text-gray-500">Chain: {wallet.chainId}</p>
                  )}
                </div>
                <button
                  onClick={disconnectWallet}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition"
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={connectWallet}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg transition font-semibold"
                >
                  🦊 Connect Wallet
                </button>
                <button
                  onClick={testWithoutWallet}
                  className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition text-sm"
                  title="Demo mode - view only"
                >
                  🎭 Demo
                </button>
              </div>
            )}
          </div>
        </div>
        {error && (
          <div className="mt-4 p-4 bg-red-900/50 border border-red-500 rounded">
            <p className="text-red-200">⚠️ {error}</p>
            <p className="text-sm text-red-300 mt-2">Make sure Hardhat node is running on port 8545</p>
          </div>
        )}
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Trades" value={stats.totalTrades} />
        <StatCard title="Total Profit" value={`$${stats.totalProfit.toFixed(2)}`} />
        <StatCard title="Win Rate" value={`${stats.winRate.toFixed(1)}%`} />
        <StatCard title="Active Positions" value={stats.activePositions} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
          <div className="space-y-3">
            <TradeItem strategy="Arbitrage" profit={12.5} time="2 min ago" />
            <TradeItem strategy="Yield Optimization" profit={8.3} time="15 min ago" />
            <TradeItem strategy="Risk Management" profit={-2.1} time="1 hour ago" />
          </div>
          <p className="text-sm text-gray-500 mt-4">
            💡 Showing demo trades. Real trades will appear once agent executes them.
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Agent Status</h2>
          <div className="space-y-4">
            <StatusItem label="Agent ID" value={agentStatus.agentId.toString()} />
            <StatusItem 
              label="Status" 
              value={agentStatus.status} 
              color={agentStatus.status === "Active" ? "green" : "gray"} 
            />
            <StatusItem label="Reputation Score" value={`${agentStatus.reputationScore}/100`} />
            <StatusItem label="Validations" value={`${agentStatus.validations} passed`} />
          </div>
          <button 
            onClick={loadData}
            disabled={refreshing}
            className={`mt-6 w-full text-white py-2 px-4 rounded transition font-semibold ${
              refreshing 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {refreshing ? '⏳ Refreshing...' : '🔄 Refresh Data'}
          </button>
          {lastRefresh && (
            <p className="text-xs text-gray-500 text-center mt-2">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>

      {/* Feedback Section */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">📝 Submit Feedback (ERC-8004)</h2>
        <p className="text-gray-400 mb-4">Rate the agent's performance and submit on-chain feedback</p>
        
        <div className="flex items-center gap-4 mb-4">
          <label className="text-sm font-medium">Rating: {feedbackValue}/100</label>
          <input
            type="range"
            min="0"
            max="100"
            value={feedbackValue}
            onChange={(e) => setFeedbackValue(Number(e.target.value))}
            className="flex-1"
            disabled={!wallet.connected}
          />
          <span className="text-2xl">
            {feedbackValue >= 80 ? '😊' : feedbackValue >= 50 ? '😐' : '😞'}
          </span>
        </div>

        <button
          onClick={submitFeedback}
          disabled={!wallet.connected || submitting}
          className={`w-full py-3 rounded-lg font-semibold transition ${
            wallet.connected && !submitting
              ? 'bg-green-600 hover:bg-green-700'
              : 'bg-gray-600 cursor-not-allowed'
          }`}
        >
          {submitting ? '⏳ Submitting...' : wallet.connected ? '✅ Submit Feedback' : '🔒 Connect Wallet to Submit'}
        </button>

        {wallet.connected && (
          <p className="text-xs text-gray-500 mt-2">
            Connected as: {wallet.address}
          </p>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <p className="text-gray-400 text-sm mb-2">{title}</p>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}

function TradeItem({ strategy, profit, time }: { strategy: string; profit: number; time: string }) {
  const isProfit = profit > 0;
  return (
    <div className="flex justify-between items-center p-3 bg-gray-700 rounded">
      <div>
        <p className="font-medium">{strategy}</p>
        <p className="text-sm text-gray-400">{time}</p>
      </div>
      <p className={`font-bold ${isProfit ? "text-green-400" : "text-red-400"}`}>
        {isProfit ? "+" : ""}{profit.toFixed(2)}%
      </p>
    </div>
  );
}

function StatusItem({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-gray-400">{label}</span>
      <span className={`font-medium ${color === "green" ? "text-green-400" : ""}`}>{value}</span>
    </div>
  );
}
