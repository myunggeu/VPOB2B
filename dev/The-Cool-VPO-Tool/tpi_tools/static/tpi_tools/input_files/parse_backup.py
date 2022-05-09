import os

files = (os.listdir("backup"))
with open("out.csv", 'w') as outf:
	outf.write("TP,Location,Visid,Explanation\n")
	for file in files:
		tp_name_loc = file.split("_")[8]
		current_loc = tp_name_loc.split("@")[0]
		current_tp = tp_name_loc.split("@")[1].replace(".txt", "")
		print(current_loc, current_tp)
		with open("backup/{}".format(file), 'r') as bfile:
			for line in bfile:
				if len(line.split(",")) < 3:
					continue
				visid = line.split("Explanation: ")[0].split(" ")[1].replace(",", "")
				explanation = line.split("Explanation: ")[1]
				print(visid)
				outf.write("{},{},{},{},{}\n".format(current_tp, current_loc, visid, explanation.replace("\n", ""), file))

