
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
