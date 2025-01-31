**🦟 West Nile Virus Detective: Track the Virus with Nextstrain! 🌍**  

Hi there! This guide will help you use Nextstrain—a powerful tool for tracking virus evolution—to study West Nile Virus (WNV) in Nebraska and across the US. No advanced bioinformatics experience needed!  

---

### **📦 What You’ll Need**  
1. **Tools to Install**:  
   - **Conda**: A package manager to organize your tools. Download here: [Conda Installation Guide](https://docs.conda.io/en/latest/miniconda.html).  
   - **Nextstrain Tools**: `Augur` (for data analysis) and `Auspice` (for visualization).  

2. **Input Files**:  
   - **Virus Genetic Data** (`sequences.fasta`): Contains RNA sequences of the virus.  
   - **Virus Metadata** (`metadata.tsv`): Includes details like collection dates and locations.  

---

### **🚀 Step-by-Step Guide**  

#### **Step 1: Set Up Your Environment with Conda**  
**Goal**: Install Conda and Nextstrain tools.  

1. **Install Conda**: Follow the official guide linked above.  
2. **Install Augur**:  
   ```bash  
   git clone https://github.com/nextstrain/augur.git  # Clones the Augur repository  
   cd augur  
   conda env create -f environment.yml  # Creates a Conda environment  
   export NCBI_EMAIL=<YOUR_EMAIL_HERE>  # Required for data downloads  
   ```  
3. **Activate the Conda Environment**:  
   ```bash  
   conda activate augur  
   ```  
4. **Install Auspice**:  
   ```bash  
   conda install -c conda-forge nodejs  # Installs Node.js  
   npm install --global auspice  # Installs Auspice globally  
   ```  
5. **Verify Installations**:  
   ```bash  
   augur -h  # Displays help menu for Augur  
   auspice -h  # Displays help menu for Auspice  
   ```  
   *Expected Outcome*: Help menus confirm both tools are installed.  

---

#### **Step 2: Download the Project Files**  
**Goal**: Get the West Nile Virus analysis toolkit.  
```bash  
git clone https://github.com/ZachPella/West-Nile-Virus-nextstrain.git  
cd WNV_build_test_gitversion  
```  
*What Happens*: This downloads the project files into a folder named `WNV_build_test_gitversion`.  

---

#### **Step 3: Run the Analysis Pipeline**  
**Goal**: Generate interactive visualizations of the virus’s spread.  

1. **Clear Previous Results (Optional)**:  
   ```bash  
   snakemake clean  # Removes old files to start fresh  
   ```  
2. **Execute the Analysis**:  
   ```bash  
   snakemake --cores all  # Runs the full pipeline (takes ~40 minutes)  
   ```  
   *What Happens*: The pipeline analyzes genetic data, builds evolutionary trees, and prepares maps.  

---

### **📂 Project Structure Explained**  
```  
WNV_build_test_gitversion/  
├── config/                 # Configuration files  
│   ├── WNV_reference.gb    # Reference genome for analysis  
│   ├── auspice_config.json # Visualization settings  
│   ├── colors_clean.py     # Color schemes for virus groups  
│   └── lat_longs_clean.tsv # Geographic coordinates  
├── data/                   # Input data  
│   ├── metadata.tsv        # Virus sample details  
│   └── sequences.fasta     # Genetic sequences  
├── scripts/                # Custom scripts for data processing  
├── results/                # Output files (generated after analysis)  
└── Snakefile               # Workflow instructions for Snakemake  
```  

---

### **📊 Expected Outputs**  
1. **Interactive Maps**: Visualize the geographic spread of WNV.  
2. **Evolutionary Trees**: Explore how virus strains are related over time.  
3. **County-Level Insights**: Track WNV activity in Nebraska counties.  

---

### **🔍 View Your Results**  
**Goal**: Launch a local web server to explore results.  
```bash  
auspice view --datasetDir ./auspice  
```  
*What Happens*: A link (e.g., `http://localhost:4000`) will appear. Open it in your browser to interact with the data!  

---

### **⚠️ Troubleshooting Tips**  
- **Missing Files**: Confirm `sequences.fasta` and `metadata.tsv` are in the `data/` folder.  
- **Permission Issues**: Ensure you have write access to the project directory.  
- **Errors**: Check the `logs/` folder for error details. Contact your IT support if needed.  

---

### **🌟 Credits**  
- **Nextstrain Team**: [Nextstrain.org](https://nextstrain.org)  
- **WestNile 4K Project**: Original project framework.  
- **UNMC Dr. Fauver Lab**: For their research on West Nile Virus.  

---

**Congratulations!** You’ve successfully mapped the spread of West Nile Virus. Share your findings with colleagues or explore other viruses on Nextstrain!  

*Note: Some steps (e.g., Conda setup) may require assistance from your IT team.* 😊
