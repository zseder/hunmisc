import sys



def filter_fs(problem_f_handler, not_needed_list, orig_num_fname,
        filtered_name ):
    
    a = open('{0}.problem'.format(filtered_name), 'w')
   
    
    orig_new_nums = {}
    new_num_fname = {}
    max_new_value = 0 
    not_needed_feats = set(not_needed_list)
    for l in problem_f_handler:
        needed_data = []
        data = l.strip().split(' ')
        needed_data.append(data[0])
        for d in data[1:]:
            index, value = d.split(':')
            if index not in not_needed_feats:
                if index not in orig_new_nums:    
                    max_new_value += 1
                    orig_new_nums[index] = max_new_value
                    new_num_fname[max_new_value] = orig_num_fname[index]
                needed_data.append('{0}:{1}'.format(orig_new_nums[index],
                    value))    
        a.write('{0}\n'.format(' '.join(needed_data)))            
               
    b = open('{0}.featureNumbers'.format(filtered_name), 'w')      
    for i in new_num_fname:
        b.write('{0}\t{1}\n'.format(new_num_fname[i], i))
    b.close()

def main():
   filter_fs(open(sys.argv[1]), [ l.strip() for l in
           open(sys.argv[2]).readlines()], dict([(l.strip().split('\t')[1],
               l.strip().split('\t')[0]) for l in open(sys.argv[3])]),
           sys.argv[4])

if __name__ == "__main__":
    main()
