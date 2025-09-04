
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
