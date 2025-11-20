import os

train_folder = r"C:\Users\ny111\OneDrive\Desktop\Nishant Rajput\Leaf_Dataset\leaf_dataset\train"
out_file = "classes.py"

classes = sorted([
    d for d in os.listdir(train_folder)
    if os.path.isdir(os.path.join(train_folder, d))
])

with open(out_file, "w", encoding="utf-8") as f:
    f.write("# Auto-generated classes file\n")
    f.write("leaf_classes = [\n")
    for c in classes:
        f.write(f'    "{c}",\n')
    f.write("]\n")

print("Created", out_file, "with", len(classes), "classes.")
