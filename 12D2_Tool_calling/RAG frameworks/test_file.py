section = "Refrigerated Depot - Section X"
mapping = {
    "section x": "Representative Mwangi",
    "section y": "Representative Otieno"
}
section_lower = section.lower()
for key, rep in mapping.items():
    if key in section_lower:
        print(rep)
        break
else:
    print("No representative found.")