
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
