def find_labels(filename):
	label_list = []
	with open(filename, 'r+') as f:
		lines = f.readlines()
		for line in lines:
			line = line.strip().split("\t")
			line[1] = ("").join(line[1].split(","))
			if int(line[1]) > 500:
				labels = line[0]
				label_list.append(labels)
		return label_list


find_labels('breeds.csv')

def find_datasets(filename):
	dataset_list = []
	with open(filename, 'r+') as f:
		lines = f.readlines()
		for line in lines:
			line = line.strip().split("\t")
			line[1] = ("").join(line[1].split(","))
			datasets = line[1]
			if int(datasets) > 500:
				dataset_list.append(datasets)
		return dataset_list
			

find_datasets('breeds.csv')