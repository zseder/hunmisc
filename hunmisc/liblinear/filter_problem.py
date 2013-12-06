import sys



def filter_fs(problem_f_handler, needed_features_list, orig_num_fname,
              needed_labels_list, orig_num_labelname, filtered_name):
    
    a = open('{0}.problem'.format(filtered_name), 'w')
   
    
    orig_new_nums = {}
    new_num_fname = {}
    orig_new_labelnums = {}
    new_num_labelname = {}
    max_new_value = 0 
    max_new_labelvalue = -1
    needed_feats = set(needed_features_list)
    needed_labels = set(needed_labels_list)
    for l in problem_f_handler:
        
        data = l.strip().split(' ')
        label_index = str(data[0])
          
        if label_index in needed_labels:
            if label_index not in orig_new_labelnums:
                max_new_labelvalue += 1
                orig_new_labelnums[label_index] = max_new_labelvalue
                new_num_labelname[max_new_labelvalue] =\
                        orig_num_labelname[label_index] 

            needed_data = []  
            for d in data[1:]:
                index, value = d.split(':')
                if index in needed_feats:
                    if index not in orig_new_nums:    
                        max_new_value += 1
                        orig_new_nums[index] = max_new_value
                        new_num_fname[max_new_value] = orig_num_fname[index]
                    needed_data.append('{0}:{1}'.format(orig_new_nums[index],
                        value))    
            needed_data.sort(key=lambda x:int(x.split(':')[0]))        
            a.write('{0} {1}\n'.format(orig_new_labelnums\
                             [label_index], ' '.join(needed_data)))            
    
    a.close()

    b = open('{0}.featureNumbers'.format(filtered_name), 'w')      
    for i in new_num_fname:
        b.write('{0}\t{1}\n'.format(new_num_fname[i], i))
    b.close()
    
    c = open('{0}.labelNumbers'.format(filtered_name), 'w')
    for i in new_num_labelname:
        c.write('{0}\t{1}\n'.format(new_num_labelname[i], i))
    c.close()    

def main():
   
   orig_name = sys.argv[1]
   problem_file = '{0}.problem'.format(orig_name)
   #nums_of_needed_features_file = sys.argv[2]
   orig_feature_name_nums_file = '{0}.featureNumbers'.format(orig_name)
   orig_label_nums_file = '{0}.labelNumbers'.format(orig_name)
   name_of_resulting = sys.argv[2]

   filter_fs(open(problem_file), [ l.strip().split('\t')[1] for l in
           open(orig_feature_name_nums_file).readlines()],\
           dict([(l.strip().split('\t')[1],l.strip().split('\t')[0])
           for l in open(orig_feature_name_nums_file)]), [ str(0), str(9), str(11)], #needed_label_nums
           dict([(l.strip().split('\t')[1],l.strip().split('\t')[0])
           for l in open(orig_label_nums_file)]), name_of_resulting)

if __name__ == "__main__":
    main()
