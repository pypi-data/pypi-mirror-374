import numpy as np
import pandas as pd
import collections
import json
import requests
import zipfile
import os
import io

global_tree = dict()
lineage_to_keep = dict()
seen_lineages = set()

def get_global_tree(tree, parent=None):
    if parent not in global_tree:
        global_tree[parent] = set()
    if "children" in tree.keys():
        for child in tree["children"]:
            get_global_tree(child, tree["node_attrs"]["Nextclade_pango"]["value"])
    global_tree[parent].add(tree["node_attrs"]["Nextclade_pango"]["value"])


#generate lineage to keep based on variant_list and global_tree 
#(if a variant is in variant_list, keep all lineages in the same branch)
def get_lineage_to_keep(parent, lineage, variant_list ):
    if parent not in lineage_to_keep and parent in variant_list:
        lineage_to_keep[parent] = set()
    if parent in variant_list:
        lineage_to_keep[parent].add(lineage)  
    if lineage not in seen_lineages and lineage in global_tree :
        seen_lineages.add(lineage)
        for child in global_tree[lineage]:
            if child not in variant_list:
                get_lineage_to_keep(lineage, child, variant_list)
                

def download_extract_load_files(url, zip_filename='Full_data_latest.zip'):
    """
    Downloads a zip file from the given URL (if not already present),
    extracts all files to a 'downloaded_data' directory,
    and loads specific files as requested.
    
    Args:
    url (str): The URL of the zip file to download.
    zip_filename (str): The name of the zip file (default is 'Full_data_latest.zip').
    
    Returns:
    tuple: (pandas DataFrame of Full_data_latest.csv, 
            dict from tree.json, 
            list from variant_list.txt)
    """
    # Create downloaded_data directory if it doesn't exist
    download_dir = 'downloaded_data'
    os.makedirs(download_dir, exist_ok=True)
    
    zip_path = os.path.join(download_dir, zip_filename)
    
    # Check if zip file already exists
    if os.path.exists(zip_path):
        user_input = input(f"{zip_filename} already exists. Do you want to redownload? (y/n): ").lower()
        if user_input != 'y':
            print("Using existing files...")
            return load_files(download_dir)

    try:
        # Download the zip file
        print("Downloading zip file...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save the zip file
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract all files from the zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        
        print("Files extracted successfully.")
        
        return load_files(download_dir)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
    except zipfile.BadZipFile:
        print("The downloaded file is not a valid zip file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None, None, None

def load_files(directory):
    """
    Loads specific files from the given directory.
    
    Args:
    directory (str): Path to the directory containing the files.
    
    Returns:
    tuple: (pandas DataFrame of Full_data_latest.csv, 
            dict from tree.json, 
            list from variant_list.txt)
    """
    # Load Full_data_latest.csv
    csv_path = os.path.join(directory, 'Full_data_latest.csv')
    df = pd.read_csv(csv_path)
    print("Loaded Full_data_latest.csv")

    # Load tree.json
    json_path = os.path.join(directory, 'tree.json')
    with open(json_path, 'r') as json_file:
        tree_data = json.load(json_file)
    print("Loaded tree.json")

    # Load variant_list.txt
    variant_list = []
    txt_path = os.path.join(directory, 'variant_list.txt')
    with open(txt_path, 'r') as f:
        for line in f:
            variant_list.append(line.strip())
    print("Loaded variant_list.txt")

    return df, tree_data, variant_list

def generate_M(path_full_data, path_tree, path_variant_list, path_output, min_freq_filter=0.5, min_num_seq_filter=5):
    global global_tree
    global seen_lineages
    global lineage_to_keep
    
    if path_full_data.startswith("http"):
        full_data, data, variant_list = download_extract_load_files(path_full_data)

    if not path_full_data.startswith("http") and path_full_data.endswith(".zip"):
        with zipfile.ZipFile(path_full_data, 'r') as zip_ref:
            zip_ref.extractall("downloaded_data")
        full_data, data, variant_list = load_files("downloaded_data")
        
    if path_full_data.endswith(".csv"):
        full_data = pd.read_csv(path_full_data)
    if path_tree.endswith(".json"):
        with open(path_tree, 'r') as json_file:
            data = json.load(json_file)
    if path_variant_list.endswith(".txt"):
        variant_list = []
        with open(path_variant_list, 'r') as f:
            variant_list = []
            for line in f:
                variant_list.append(line.strip())
    
    print("M generation started, please wait... (it may take a few minutes)")        
    get_global_tree(data['tree'])

    all_lineages = set()
    for k, v in global_tree.items():
        all_lineages = all_lineages.union(v)
        
            
            
    for var in variant_list:
        
        seen_lineages = set()
        get_lineage_to_keep(var, var, variant_list)
    list_lineage_to_keep_flatted = []
    for k, v in lineage_to_keep.items():
        list_lineage_to_keep_flatted += list(v)
        
    # clean substitutions colum by forcing that all value are list to be able to aply data.substitutions.sum()
    data = full_data[full_data["Lineage"].isin(list_lineage_to_keep_flatted)]
    #remove rows with empty substitutions or nan
    data = data[data["substitutions"] != ""]
    data = data[data["substitutions"].notna()]

    data.substitutions = data.substitutions.str.split(",")
    problem_row = []
    for i, value in enumerate(data.substitutions):
        if type(value) is not list or value == []:
            # print("in position ", i, " the value: ", value, "is not a list")
            problem_row.append(i)
            # fix it
            data.at[i, "substitutions"] = []
            
    uniq_mutation = np.unique(np.concatenate(data.substitutions.to_numpy()))


    # creat the variant matrix where each row represent a specific mutations
    # and each col represent a variant and the value of variants_matrix[i, j] is the likelhood that
    # the variation j will have the mutation i, there for it's between 0 and 1.
    result = pd.DataFrame(0.0, index=uniq_mutation, columns=data.Lineage.unique())
    result["position"] = [int(e[1:-1]) for e in uniq_mutation]
    result = result.sort_values(by="position")
    #drop position col
    result = result.drop("position", axis=1)

    for variant in result.columns:
        sub_df = data[data.Lineage == variant]
        # print("variant: ", variant, " has ", sub_df.shape[0], " sequences")
        # print("sub_df shape: ", sub_df.shape)
        nb_seq = sub_df.shape[0]
        temp_mut = np.concatenate(sub_df.substitutions.to_numpy())
        ctr = collections.Counter(temp_mut)  # calculate all freq
        for mut in ctr:
            result.at[mut, variant] = ctr[mut] / nb_seq
    # print("out of loop")
    result = result.T
    ctr_variant = collections.Counter(data.Lineage)
    result["Count"] = [ctr_variant[variant] for variant in result.index]

    # result.to_csv("raw_result.csv", index=True, encoding="utf-8-sig")
    result_filtered = result.copy()

    for lineage in lineage_to_keep:
        #get all children of lineage
        children = list(set(lineage_to_keep[lineage]).intersection(result.index))
        # print("lineage: ", lineage)
        # print("children: ", children)
        #recalculate the weighted mean (by Count) of the children and put it in lineage row and put Count of lineage in Count row
        if children != []:
            result_filtered.loc[lineage, result.columns[:-1]] = result.loc[children, result.columns[:-1]].mul(result.loc[children]["Count"], axis=0).sum() / result.loc[children]["Count"].sum()
            result_filtered.loc[lineage, "Count"] = result.loc[children]["Count"].sum()
            #remove children from result
            children.remove(lineage)
            # print("Lilineage: ", lineage, " has ", len(children), " children")
            if children != []:
                result_filtered = result_filtered.drop(children)
                
    #keep only lineage (variant) with more than 5 sequences
    result_filtered = result_filtered[result_filtered.Count > min_num_seq_filter]

    #drop count columns
    result_filtered = result_filtered.drop(["Count"], axis=1)

    # keep only mutation that have atleast one lineage with freq value > 0.5
    result_filtered = result_filtered.loc[:, (result_filtered > min_freq_filter).any(axis=0)]

    # Export Result
    result_filtered.to_csv(path_output, encoding="utf-8-sig")
    
