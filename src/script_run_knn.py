from change_interpreter.knn import KNN
knn = KNN()
#knn.drop_projection('knn_no_entity')
#result_p = knn.projection_query_knn_no_entity()
#print("*****+ Result Projection Query **********")
#print(result_p)
r = knn.run_knn_filtered()
print(r)
#result_k = knn.run_cluster_write_no_entity()
print("*****+ Result KNN **********")
result = knn.write_similarity()
print(result)



