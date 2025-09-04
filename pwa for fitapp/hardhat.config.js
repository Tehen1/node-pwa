
require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-etherscan");

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    polygonZkEVM: {
      url: "https://zkevm-rpc.com",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 1101,
      gasPrice: 1000000000 // 1 gwei
    },
    polygonZkEVMTestnet: {
      url: "https://rpc.public.zkevm-test.net",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 1442,
      gasPrice: 1000000000
    }
  },
  etherscan: {
    apiKey: {
      polygonZkEVM: process.env.ZKEVM_API_KEY || "abc",
      polygonZkEVMTestnet: process.env.ZKEVM_API_KEY || "abc"
    },
    customChains: [
      {
        network: "polygonZkEVM",
        chainId: 1101,
        urls: {
          apiURL: "https://api-zkevm.polygonscan.com/api",
          browserURL: "https://zkevm.polygonscan.com"
        }
      },
      {
        network: "polygonZkEVMTestnet", 
        chainId: 1442,
        urls: {
          apiURL: "https://api-testnet-zkevm.polygonscan.com/api",
          browserURL: "https://testnet-zkevm.polygonscan.com"
        }
      }
    ]
  }
};
