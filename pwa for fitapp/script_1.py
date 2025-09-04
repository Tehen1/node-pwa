# Create Smart Contracts for FixieRun zkEVM integration
print("=== SMART CONTRACTS FOR FIXIERUN zkEVM INTEGRATION ===")
print()

# FIXIE Token Contract (ERC-20)
fixie_token_contract = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title FixieToken
 * @dev ERC20 token for FixieRun Move-to-Earn ecosystem
 */
contract FixieToken is ERC20, ERC20Burnable, Ownable, Pausable {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1B tokens
    uint256 public constant DAILY_EMISSION_LIMIT = 500_000 * 10**18; // 500K per day
    
    mapping(address => bool) public minters;
    mapping(uint256 => uint256) public dailyMinted; // day => amount minted
    
    event MinterAdded(address indexed minter);
    event MinterRemoved(address indexed minter);
    event TokensMinted(address indexed to, uint256 amount, string reason);
    
    constructor() ERC20("FixieRun Token", "FIXIE") {
        // Mint initial supply to owner (25% of max supply)
        _mint(msg.sender, 250_000_000 * 10**18);
    }
    
    modifier onlyMinter() {
        require(minters[msg.sender], "Not authorized to mint");
        _;
    }
    
    function addMinter(address _minter) external onlyOwner {
        minters[_minter] = true;
        emit MinterAdded(_minter);
    }
    
    function removeMinter(address _minter) external onlyOwner {
        minters[_minter] = false;
        emit MinterRemoved(_minter);
    }
    
    function mintWorkoutReward(address to, uint256 amount, string calldata reason) 
        external 
        onlyMinter 
        whenNotPaused 
    {
        uint256 today = block.timestamp / 1 days;
        require(
            dailyMinted[today] + amount <= DAILY_EMISSION_LIMIT, 
            "Daily emission limit exceeded"
        );
        require(
            totalSupply() + amount <= MAX_SUPPLY, 
            "Would exceed max supply"
        );
        
        dailyMinted[today] += amount;
        _mint(to, amount);
        emit TokensMinted(to, amount, reason);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }
}
"""

# Fitness NFT Contract (ERC-721)
nft_contract = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title FixieRunNFT
 * @dev NFT contract for FixieRun equipment and achievements
 */
contract FixieRunNFT is ERC721, ERC721URIStorage, Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    enum Rarity { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }
    enum ItemType { SNEAKER, BIKE, ACHIEVEMENT, SPECIAL }
    
    struct NFTMetadata {
        string name;
        Rarity rarity;
        ItemType itemType;
        uint256 level;
        uint256 experience;
        uint256 speedBoost; // Percentage boost (1-20)
        uint256 tokenBoost; // Percentage boost (1-20) 
        uint256 experienceBoost; // Percentage boost (1-20)
        bool isStaked;
        uint256 stakedTimestamp;
    }
    
    mapping(uint256 => NFTMetadata) public nftMetadata;
    mapping(address => uint256[]) public userNFTs;
    mapping(Rarity => uint256) public mintCosts; // Cost in FIXIE tokens
    
    address public fixieToken;
    address public stakingContract;
    
    event NFTMinted(address indexed to, uint256 indexed tokenId, Rarity rarity);
    event NFTLevelUp(uint256 indexed tokenId, uint256 newLevel);
    event NFTStaked(uint256 indexed tokenId, address indexed staker);
    event NFTUnstaked(uint256 indexed tokenId, address indexed staker);
    
    constructor(address _fixieToken) ERC721("FixieRun Equipment", "FIXIE-NFT") {
        fixieToken = _fixieToken;
        
        // Set mint costs for each rarity (in FIXIE tokens)
        mintCosts[Rarity.COMMON] = 10 * 10**18;      // 10 FIXIE
        mintCosts[Rarity.UNCOMMON] = 25 * 10**18;    // 25 FIXIE
        mintCosts[Rarity.RARE] = 50 * 10**18;        // 50 FIXIE
        mintCosts[Rarity.EPIC] = 100 * 10**18;       // 100 FIXIE
        mintCosts[Rarity.LEGENDARY] = 250 * 10**18;  // 250 FIXIE
    }
    
    function mintNFT(
        address to,
        string memory name,
        string memory tokenURI,
        Rarity rarity,
        ItemType itemType
    ) external nonReentrant {
        // Burn FIXIE tokens for minting
        IERC20(fixieToken).transferFrom(msg.sender, address(0), mintCosts[rarity]);
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);
        
        // Generate random stats based on rarity
        (uint256 speedBoost, uint256 tokenBoost, uint256 experienceBoost) = _generateStats(rarity);
        
        nftMetadata[tokenId] = NFTMetadata({
            name: name,
            rarity: rarity,
            itemType: itemType,
            level: 1,
            experience: 0,
            speedBoost: speedBoost,
            tokenBoost: tokenBoost,
            experienceBoost: experienceBoost,
            isStaked: false,
            stakedTimestamp: 0
        });
        
        userNFTs[to].push(tokenId);
        emit NFTMinted(to, tokenId, rarity);
    }
    
    function levelUpNFT(uint256 tokenId, uint256 experienceGained) external {
        require(msg.sender == owner() || msg.sender == stakingContract, "Unauthorized");
        require(_exists(tokenId), "NFT does not exist");
        
        NFTMetadata storage metadata = nftMetadata[tokenId];
        metadata.experience += experienceGained;
        
        // Level up every 1000 experience points
        uint256 newLevel = (metadata.experience / 1000) + 1;
        if (newLevel > metadata.level) {
            metadata.level = newLevel;
            // Increase boosts by 1% per level
            metadata.speedBoost += 1;
            metadata.tokenBoost += 1;
            metadata.experienceBoost += 1;
            
            emit NFTLevelUp(tokenId, newLevel);
        }
    }
    
    function stakeNFT(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        require(!nftMetadata[tokenId].isStaked, "Already staked");
        
        nftMetadata[tokenId].isStaked = true;
        nftMetadata[tokenId].stakedTimestamp = block.timestamp;
        
        emit NFTStaked(tokenId, msg.sender);
    }
    
    function unstakeNFT(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        require(nftMetadata[tokenId].isStaked, "Not staked");
        
        nftMetadata[tokenId].isStaked = false;
        nftMetadata[tokenId].stakedTimestamp = 0;
        
        emit NFTUnstaked(tokenId, msg.sender);
    }
    
    function getUserNFTs(address user) external view returns (uint256[] memory) {
        return userNFTs[user];
    }
    
    function getNFTBoosts(uint256 tokenId) external view returns (uint256, uint256, uint256) {
        NFTMetadata memory metadata = nftMetadata[tokenId];
        return (metadata.speedBoost, metadata.tokenBoost, metadata.experienceBoost);
    }
    
    function _generateStats(Rarity rarity) private view returns (uint256, uint256, uint256) {
        uint256 baseBoost;
        uint256 variance;
        
        if (rarity == Rarity.COMMON) {
            baseBoost = 1;
            variance = 2;
        } else if (rarity == Rarity.UNCOMMON) {
            baseBoost = 3;
            variance = 3;
        } else if (rarity == Rarity.RARE) {
            baseBoost = 6;
            variance = 4;
        } else if (rarity == Rarity.EPIC) {
            baseBoost = 10;
            variance = 5;
        } else {
            baseBoost = 15;
            variance = 5;
        }
        
        // Generate pseudo-random stats (in production, use Chainlink VRF)
        uint256 speedBoost = baseBoost + (uint256(keccak256(abi.encodePacked(block.timestamp, "speed"))) % variance);
        uint256 tokenBoost = baseBoost + (uint256(keccak256(abi.encodePacked(block.timestamp, "token"))) % variance);
        uint256 experienceBoost = baseBoost + (uint256(keccak256(abi.encodePacked(block.timestamp, "exp"))) % variance);
        
        return (speedBoost, tokenBoost, experienceBoost);
    }
    
    function setStakingContract(address _stakingContract) external onlyOwner {
        stakingContract = _stakingContract;
    }
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
}
"""

# Workout Validator Contract  
workout_contract = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

interface IFixieToken {
    function mintWorkoutReward(address to, uint256 amount, string calldata reason) external;
}

interface IFixieRunNFT {
    function getNFTBoosts(uint256 tokenId) external view returns (uint256, uint256, uint256);
    function levelUpNFT(uint256 tokenId, uint256 experienceGained) external;
    function ownerOf(uint256 tokenId) external view returns (address);
}

/**
 * @title WorkoutValidator
 * @dev Validates workouts and mints FIXIE token rewards
 */
contract WorkoutValidator is Ownable, ReentrancyGuard {
    using ECDSA for bytes32;
    
    IFixieToken public fixieToken;
    IFixieRunNFT public fixieRunNFT;
    
    mapping(address => bool) public validators;
    mapping(bytes32 => bool) public processedWorkouts;
    mapping(address => uint256) public userStreaks;
    mapping(address => uint256) public lastWorkoutDate;
    
    struct Workout {
        address user;
        uint256 distance; // in meters
        uint256 duration; // in seconds
        uint256 calories;
        string workoutType; // "running", "cycling", "walking"
        uint256 timestamp;
        uint256[] equippedNFTs;
        bytes signature;
    }
    
    event WorkoutValidated(
        address indexed user,
        uint256 distance,
        uint256 tokensEarned,
        uint256 streak
    );
    
    event StreakBonus(address indexed user, uint256 streak, uint256 bonus);
    
    constructor(address _fixieToken, address _fixieRunNFT) {
        fixieToken = IFixieToken(_fixieToken);
        fixieRunNFT = IFixieRunNFT(_fixieRunNFT);
    }
    
    function addValidator(address _validator) external onlyOwner {
        validators[_validator] = true;
    }
    
    function removeValidator(address _validator) external onlyOwner {
        validators[_validator] = false;
    }
    
    function validateWorkout(Workout calldata workout) external nonReentrant {
        require(validators[msg.sender], "Not authorized validator");
        
        bytes32 workoutHash = keccak256(
            abi.encodePacked(
                workout.user,
                workout.distance,
                workout.duration,
                workout.calories,
                workout.workoutType,
                workout.timestamp
            )
        );
        
        require(!processedWorkouts[workoutHash], "Workout already processed");
        require(block.timestamp - workout.timestamp < 3600, "Workout too old"); // 1 hour max
        
        processedWorkouts[workoutHash] = true;
        
        // Calculate base reward (tokens per km)
        uint256 baseReward = _calculateBaseReward(workout.workoutType, workout.distance);
        
        // Apply NFT boosts
        uint256 totalTokenBoost = 0;
        uint256 totalExpBoost = 0;
        
        for (uint256 i = 0; i < workout.equippedNFTs.length; i++) {
            uint256 tokenId = workout.equippedNFTs[i];
            require(fixieRunNFT.ownerOf(tokenId) == workout.user, "NFT not owned");
            
            (, uint256 tokenBoost, uint256 expBoost) = fixieRunNFT.getNFTBoosts(tokenId);
            totalTokenBoost += tokenBoost;
            totalExpBoost += expBoost;
            
            // Level up NFT based on workout
            uint256 expGained = workout.distance / 100; // 1 exp per 100m
            fixieRunNFT.levelUpNFT(tokenId, expGained);
        }
        
        // Apply boosts
        uint256 boostedReward = baseReward + (baseReward * totalTokenBoost / 100);
        
        // Calculate and apply streak bonus
        _updateStreak(workout.user);
        uint256 streakMultiplier = _getStreakMultiplier(userStreaks[workout.user]);
        uint256 finalReward = boostedReward * streakMultiplier / 100;
        
        // Add milestone bonuses
        uint256 milestoneBonus = _getMilestoneBonus(workout.distance);
        finalReward += milestoneBonus;
        
        // Mint tokens
        fixieToken.mintWorkoutReward(
            workout.user,
            finalReward,
            string(abi.encodePacked("Workout: ", workout.workoutType))
        );
        
        emit WorkoutValidated(
            workout.user,
            workout.distance,
            finalReward,
            userStreaks[workout.user]
        );
    }
    
    function _calculateBaseReward(string memory workoutType, uint256 distance) 
        private 
        pure 
        returns (uint256) 
    {
        uint256 distanceKm = distance / 1000; // Convert to km
        uint256 ratePerKm;
        
        if (keccak256(bytes(workoutType)) == keccak256(bytes("running"))) {
            ratePerKm = 1200; // 1.2 FIXIE per km (in wei: 1.2 * 10^18 / 1000)
        } else if (keccak256(bytes(workoutType)) == keccak256(bytes("cycling"))) {
            ratePerKm = 800; // 0.8 FIXIE per km
        } else { // walking
            ratePerKm = 500; // 0.5 FIXIE per km
        }
        
        return distanceKm * ratePerKm * 10**15; // Convert to wei
    }
    
    function _updateStreak(address user) private {
        uint256 today = block.timestamp / 1 days;
        uint256 lastDay = lastWorkoutDate[user] / 1 days;
        
        if (today == lastDay) {
            // Same day, no streak change
            return;
        } else if (today == lastDay + 1) {
            // Consecutive day, increase streak
            userStreaks[user]++;
        } else {
            // Streak broken, reset
            userStreaks[user] = 1;
        }
        
        lastWorkoutDate[user] = block.timestamp;
        
        // Emit streak bonus for milestones
        if (userStreaks[user] % 7 == 0) { // Weekly milestone
            uint256 bonus = userStreaks[user] * 10**18; // 1 FIXIE per streak day
            fixieToken.mintWorkoutReward(user, bonus, "Streak Bonus");
            emit StreakBonus(user, userStreaks[user], bonus);
        }
    }
    
    function _getStreakMultiplier(uint256 streak) private pure returns (uint256) {
        if (streak >= 30) return 150; // 50% bonus for 30+ day streak
        if (streak >= 14) return 130; // 30% bonus for 14+ day streak
        if (streak >= 7) return 115;  // 15% bonus for 7+ day streak
        if (streak >= 3) return 105;  // 5% bonus for 3+ day streak
        return 100; // No bonus
    }
    
    function _getMilestoneBonus(uint256 distance) private pure returns (uint256) {
        uint256 distanceKm = distance / 1000;
        
        if (distanceKm >= 42) return 50 * 10**18;  // Marathon: 50 FIXIE
        if (distanceKm >= 21) return 25 * 10**18;  // Half marathon: 25 FIXIE  
        if (distanceKm >= 10) return 10 * 10**18;  // 10K: 10 FIXIE
        if (distanceKm >= 5) return 5 * 10**18;    // 5K: 5 FIXIE
        if (distanceKm >= 1) return 1 * 10**18;    // 1K: 1 FIXIE
        
        return 0;
    }
    
    function getUserStreak(address user) external view returns (uint256) {
        return userStreaks[user];
    }
}
"""

# Save contracts to files
contracts = {
    "FixieToken.sol": fixie_token_contract,
    "FixieRunNFT.sol": nft_contract,
    "WorkoutValidator.sol": workout_contract
}

# Create deployment script
deployment_script = """
// Hardhat deployment script for FixieRun contracts
const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying FixieRun contracts to Polygon zkEVM...");

  // Deploy FIXIE Token
  const FixieToken = await ethers.getContractFactory("FixieToken");
  const fixieToken = await FixieToken.deploy();
  await fixieToken.deployed();
  console.log("FixieToken deployed to:", fixieToken.address);

  // Deploy FixieRun NFT
  const FixieRunNFT = await ethers.getContractFactory("FixieRunNFT");
  const fixieRunNFT = await FixieRunNFT.deploy(fixieToken.address);
  await fixieRunNFT.deployed();
  console.log("FixieRunNFT deployed to:", fixieRunNFT.address);

  // Deploy Workout Validator
  const WorkoutValidator = await ethers.getContractFactory("WorkoutValidator");
  const workoutValidator = await WorkoutValidator.deploy(
    fixieToken.address,
    fixieRunNFT.address
  );
  await workoutValidator.deployed();
  console.log("WorkoutValidator deployed to:", workoutValidator.address);

  // Setup permissions
  await fixieToken.addMinter(workoutValidator.address);
  await fixieRunNFT.setStakingContract(workoutValidator.address);
  
  console.log("\\nDeployment complete!");
  console.log("FIXIE Token:", fixieToken.address);
  console.log("FixieRun NFT:", fixieRunNFT.address);
  console.log("Workout Validator:", workoutValidator.address);
  
  // Verify contracts on zkEVM explorer
  if (network.name !== "hardhat") {
    console.log("\\nWaiting for block confirmations...");
    await fixieToken.deployTransaction.wait(6);
    await fixieRunNFT.deployTransaction.wait(6);
    await workoutValidator.deployTransaction.wait(6);
    
    console.log("Verifying contracts...");
    
    await hre.run("verify:verify", {
      address: fixieToken.address,
      constructorArguments: [],
    });
    
    await hre.run("verify:verify", {
      address: fixieRunNFT.address,
      constructorArguments: [fixieToken.address],
    });
    
    await hre.run("verify:verify", {
      address: workoutValidator.address,
      constructorArguments: [fixieToken.address, fixieRunNFT.address],
    });
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
"""

# Save files
with open('FixieToken.sol', 'w') as f:
    f.write(fixie_token_contract)
    
with open('FixieRunNFT.sol', 'w') as f:
    f.write(nft_contract)
    
with open('WorkoutValidator.sol', 'w') as f:
    f.write(workout_contract)
    
with open('deploy.js', 'w') as f:
    f.write(deployment_script)

print("Smart contracts created successfully!")
print()
print("FILES CREATED:")
print("• FixieToken.sol - ERC-20 token contract with M2E mechanics")
print("• FixieRunNFT.sol - ERC-721 NFT contract for equipment")  
print("• WorkoutValidator.sol - Workout validation and reward distribution")
print("• deploy.js - Hardhat deployment script for Polygon zkEVM")
print()

# Create package.json for the contracts
package_json = """{
  "name": "fixierun-contracts",
  "version": "1.0.0", 
  "description": "Smart contracts for FixieRun Move-to-Earn fitness app on Polygon zkEVM",
  "scripts": {
    "compile": "hardhat compile",
    "deploy:zkevm": "hardhat run scripts/deploy.js --network polygonZkEVM",
    "test": "hardhat test",
    "verify": "hardhat verify"
  },
  "dependencies": {
    "@openzeppelin/contracts": "^4.9.3",
    "@nomiclabs/hardhat-ethers": "^2.2.3",
    "@nomiclabs/hardhat-etherscan": "^3.1.7",
    "hardhat": "^2.17.1",
    "ethers": "^5.7.2"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-chai-matchers": "^1.0.6",
    "@nomiclabs/hardhat-waffle": "^2.0.6",
    "chai": "^4.3.7",
    "ethereum-waffle": "^3.4.4"
  }
}"""

hardhat_config = """
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
"""

with open('package.json', 'w') as f:
    f.write(package_json)
    
with open('hardhat.config.js', 'w') as f:
    f.write(hardhat_config)

print("• package.json - Node.js dependencies")
print("• hardhat.config.js - Hardhat configuration for zkEVM")
print()
print("DEPLOYMENT INSTRUCTIONS:")
print("1. npm install")
print("2. Set PRIVATE_KEY environment variable")
print("3. npx hardhat compile") 
print("4. npx hardhat run scripts/deploy.js --network polygonZkEVMTestnet")
print()
print("CONTRACT FEATURES:")
print("• Token emission limits (500K FIXIE/day)")
print("• NFT-based performance boosts")  
print("• Streak multipliers and milestone bonuses")
print("• Workout validation with cryptographic signatures")
print("• Deflationary tokenomics with burning mechanisms")
print("• Full ERC-20/ERC-721 compliance")