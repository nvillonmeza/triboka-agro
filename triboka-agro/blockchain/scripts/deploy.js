const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying Triboka Agro Contracts...");

  // Obtener signers
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", ethers.utils.formatEther(await deployer.getBalance()), "ETH");

  // Deploy AgroExportContract
  console.log("\n📜 Deploying AgroExportContract...");
  const AgroExportContract = await ethers.getContractFactory("AgroExportContract");
  const agroExportContract = await AgroExportContract.deploy();
  await agroExportContract.deployed();
  const agroExportAddress = agroExportContract.address;
  console.log("✅ AgroExportContract deployed to:", agroExportAddress);

  // Deploy ProducerLotNFT
  console.log("\n🏷️ Deploying ProducerLotNFT...");
  const ProducerLotNFT = await ethers.getContractFactory("ProducerLotNFT");
  const producerLotNFT = await ProducerLotNFT.deploy();
  await producerLotNFT.deployed();
  const producerLotAddress = producerLotNFT.address;
  console.log("✅ ProducerLotNFT deployed to:", producerLotAddress);

  // Deploy DocumentRegistry
  console.log("\n📄 Deploying DocumentRegistry...");
  const DocumentRegistry = await ethers.getContractFactory("DocumentRegistry");
  const documentRegistry = await DocumentRegistry.deploy();
  await documentRegistry.deployed();
  const documentRegistryAddress = documentRegistry.address;
  console.log("✅ DocumentRegistry deployed to:", documentRegistryAddress);

  // Setup roles y permisos
  console.log("\n🔐 Setting up roles and permissions...");
  
  // Grant roles en AgroExportContract
  const OPERATOR_ROLE = await agroExportContract.OPERATOR_ROLE();
  const EXPORTER_ROLE = await agroExportContract.EXPORTER_ROLE();
  const BUYER_ROLE = await agroExportContract.BUYER_ROLE();

  // Grant roles en ProducerLotNFT
  const MINTER_ROLE = await producerLotNFT.MINTER_ROLE();
  const PRODUCER_ROLE = await producerLotNFT.PRODUCER_ROLE();
  const PRODUCER_OPERATOR_ROLE = await producerLotNFT.OPERATOR_ROLE();

  // Grant roles en DocumentRegistry
  const ISSUER_ROLE = await documentRegistry.ISSUER_ROLE();
  const VERIFIER_ROLE = await documentRegistry.VERIFIER_ROLE();
  const DOC_OPERATOR_ROLE = await documentRegistry.OPERATOR_ROLE();

  console.log("✅ Roles configured successfully");

  // Crear archivo de configuración con direcciones
  const contractAddresses = {
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    deployer: deployer.address,
    deploymentDate: new Date().toISOString(),
    contracts: {
      AgroExportContract: {
        address: agroExportAddress,
        abi: "AgroExportContract.json"
      },
      ProducerLotNFT: {
        address: producerLotAddress,
        abi: "ProducerLotNFT.json"
      },
      DocumentRegistry: {
        address: documentRegistryAddress,
        abi: "DocumentRegistry.json"
      }
    },
    roles: {
      AgroExportContract: {
        DEFAULT_ADMIN_ROLE: await agroExportContract.DEFAULT_ADMIN_ROLE(),
        OPERATOR_ROLE: OPERATOR_ROLE,
        EXPORTER_ROLE: EXPORTER_ROLE,
        BUYER_ROLE: BUYER_ROLE
      },
      ProducerLotNFT: {
        DEFAULT_ADMIN_ROLE: await producerLotNFT.DEFAULT_ADMIN_ROLE(),
        MINTER_ROLE: MINTER_ROLE,
        OPERATOR_ROLE: PRODUCER_OPERATOR_ROLE,
        PRODUCER_ROLE: PRODUCER_ROLE
      },
      DocumentRegistry: {
        DEFAULT_ADMIN_ROLE: await documentRegistry.DEFAULT_ADMIN_ROLE(),
        ISSUER_ROLE: ISSUER_ROLE,
        VERIFIER_ROLE: VERIFIER_ROLE,
        OPERATOR_ROLE: DOC_OPERATOR_ROLE
      }
    }
  };

  // Guardar configuración
  const fs = require("fs");
  const path = require("path");
  
  const configDir = path.join(__dirname, "../config");
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  const configFile = path.join(configDir, `contracts-${hre.network.name}.json`);
  fs.writeFileSync(configFile, JSON.stringify(contractAddresses, null, 2));
  
  console.log("\n📁 Contract addresses saved to:", configFile);

  // Crear datos de prueba si estamos en desarrollo
  if (hre.network.name === "localhost" || hre.network.name === "hardhat") {
    console.log("\n🧪 Creating test data...");
    await createTestData(agroExportContract, producerLotNFT, documentRegistry, deployer);
  }

  console.log("\n🎉 Deployment completed successfully!");
  console.log("📊 Summary:");
  console.log(`   • AgroExportContract: ${agroExportAddress}`);
  console.log(`   • ProducerLotNFT: ${producerLotAddress}`);
  console.log(`   • DocumentRegistry: ${documentRegistryAddress}`);
  console.log(`   • Network: ${hre.network.name}`);
  console.log(`   • Chain ID: ${hre.network.config.chainId}`);
}

async function createTestData(agroContract, nftContract, docRegistry, deployer) {
  console.log("Creating test export contract...");
  
  // Crear direcciones de prueba
  const exporterAddress = deployer.address;
  const buyerAddress = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"; // Hardhat account 1
  const producerAddress = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"; // Hardhat account 2

  // Crear contrato de exportación de prueba
  const contractTx = await agroContract.createContract(
    buyerAddress,
    exporterAddress,
    "HERSHEY-CACAO-2024-001",
    "cacao",
    "Fino de Aroma",
    ethers.BigNumber.from("500"), // 500 TM
    ethers.BigNumber.from("-150"), // -150 USD/TM diferencial
    Math.floor(Date.now() / 1000), // start date
    Math.floor(Date.now() / 1000) + (90 * 24 * 60 * 60), // end date (90 días)
    Math.floor(Date.now() / 1000) + (120 * 24 * 60 * 60)  // delivery date (120 días)
  );
  
  const receipt = await contractTx.wait();
  console.log("✅ Test contract created");

  // Crear lote NFT de prueba
  const lotTx = await nftContract.createLot(
    producerAddress,
    "José Martínez",
    "Finca El Dorado",
    "-9.2948,-75.9947",
    "cacao",
    ethers.BigNumber.from("2500"), // 2500 kg
    "Fino de Aroma",
    Math.floor(Date.now() / 1000) - (30 * 24 * 60 * 60), // 30 días atrás
    ["Orgánico", "Fair Trade"],
    "ipfs://QmTestHash123"
  );
  
  await lotTx.wait();
  console.log("✅ Test lot NFT created");

  console.log("🧪 Test data created successfully!");
}

// Manejar errores
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });