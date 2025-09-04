
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

  console.log("\nDeployment complete!");
  console.log("FIXIE Token:", fixieToken.address);
  console.log("FixieRun NFT:", fixieRunNFT.address);
  console.log("Workout Validator:", workoutValidator.address);

  // Verify contracts on zkEVM explorer
  if (network.name !== "hardhat") {
    console.log("\nWaiting for block confirmations...");
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
