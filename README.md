**🦟 West Nile Virus Detective: Track the Virus with Nextstrain! 🌍**  

Hi there! This guide will help you use Nextstrain (a cool tool for tracking viruses 🕵️) to study West Nile Virus (WNV) in Nebraska and across the US. Think of it like a treasure map for viruses!  

---

### **📦 What You Need**  
1. **Your Tools**:  
   - **Conda**: A magic backpack for your tools. You need to install it!  
   - **Nextstrain Tools**: Augur and Auspice (they help analyze and visualize the virus!).  

2. **Inputs (Your Clues)**:  
   - **Virus DNA Files** (`sequences.fasta`): A file with the virus’s DNA code.  
   - **Virus Info** (`metadata.tsv`): A file with details about where and when the virus was found.  

---

### **🚀 Step-by-Step Instructions**  

#### **Step 1: Set Up Your Magic Backpack (Conda)**  
**Goal**: Install Conda and Nextstrain tools.  

1. **Install Conda**: Follow the official guide: [Conda Installation](https://docs.conda.io/en/latest/miniconda.html).  
2. **Install Augur**:  
   ```bash  
   git clone git@github.com:nextstrain/augur.git  
   cd augur  
   conda env create -f environment.yml  
   export NCBI_EMAIL=<YOUR_EMAIL_HERE>  
   ```  
3. **Activate Conda Environment**:  
   ```bash  
   conda activate augur  
   ```  
4. **Install Auspice**:  
   ```bash  
   conda install -c conda-forge nodejs  
   npm install --global auspice  
   ```  
5. **Check Your Tools**:  
   ```bash  
   augur -h  
   auspice -h  
   ```  
   *What happens?*: You’ll see help messages if everything is installed correctly!  

---

#### **Step 2: Get the Virus Detective Kit (Clone the Repository)**  
**Goal**: Download the West Nile Virus project.  
```bash  
git clone https://github.com/ZachPella/West-Nile-Virus-nextstrain.git  
cd WNV_build_test_gitversion  
```  
*What happens?*: You’ll have a folder with all the tools and files you need!  

---

#### **Step 3: Start the Virus Hunt! (Run the Build)**  
**Goal**: Analyze the virus DNA and create cool maps and graphs!  

1. **Clean Up**:  
   ```bash  
   snakemake clean  
   ```  
   *What happens?*: This removes old files to start fresh!  

2. **Run the Full Build**:  
   ```bash  
   snakemake --cores all  
   ```  
   *What happens?*: This takes about 40 minutes. It analyzes the virus DNA and creates results!  

---

### **📂 What’s Inside the Project?**  
```  
WNV_build_test_gitversion/  
├── config/                 🗺️ Maps and settings for the virus!  
│   ├── WNV_reference.gb    (The virus’s DNA map)  
│   ├── auspice_config.json (How to show the results)  
│   ├── colors_clean.py     (Colors for the virus groups)  
│   └── lat_longs_clean.tsv (Where the virus was found)  
├── data/                   🧬 Virus DNA and info!  
│   ├── metadata.tsv        (Details about the virus)  
│   └── sequences.fasta     (The virus’s DNA code)  
├── scripts/                🛠️ Tools for adding more info!  
│   ├── add_lat_long_to_metadata.py (Adds locations to the virus info)  
│   └── new_pathoplexus_data.py (Adds new virus data)  
├── results/                📊 Your results will go here!  
└── Snakefile               🐍 The recipe for the virus hunt!  
```  

---

### **🎁 What You’ll Get (Outputs!)**  
1. **Interactive Maps**: See where the virus is spreading!  
2. **Virus Family Trees**: Learn how the virus is changing over time!  
3. **County-Level Data**: Track the virus in Nebraska counties!  

---

### **🔍 View Your Results**  
**Goal**: Open the results in your browser!  
```bash  
auspice view --datasetDir ./auspice  
```  
*What happens?*: A link will appear (like `http://localhost:4000`). Open it in your browser to see the virus maps and trees!  

---

### **⚠️ Troubleshooting Tips**  
- **Missing Files**: Make sure your `sequences.fasta` and `metadata.tsv` files are in the `data/` folder!  
- **Permissions**: Ask a grown-up to check if you can write to the folder.  
- **Log Files**: If something goes wrong, check the `logs/` folder for clues!  

---

### **🌟 Credits**  
- **Nextstrain Team**: [Nextstrain.org](https://nextstrain.org)  
- **WestNile 4K Project**: The template for this project!  
- **UNMC Dr. Fauver Lab**: For their awesome work on West Nile Virus!  

---

**You did it!** Now you’re a virus detective! 🎉 Share your maps and trees with the world!  

*Note: Grown-ups might need to help install Conda or fix permissions!* 😊
