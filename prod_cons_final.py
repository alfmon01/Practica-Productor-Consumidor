from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Lock
from multiprocessing import current_process
from multiprocessing import Manager

import time, random

N = 50 #Numero de elementos que genera cada productor 
K = 15 #Numero de productores, consumidores y capacidad del buffer



#Añade elementos al buffer
def add_data(almacen, data, mutex):
    mutex.acquire()
    try:
        almacen.append(data)
        time.sleep(0.1)
    finally:
        mutex.release()


#Funcion que inserta un elemento en una lista de forma creciente      
def insertar_ordenado(lista, elem):  
    if len(lista) == 0:
        lista.append(elem)
    else:
        if elem > lista[len(lista) - 1]:
            lista.append(elem)
        else:
            temp=[]
            for i in range(len(lista)):
                if lista[i] > elem:
                        for k in lista:
                            temp.append(k)
                        lista[i] = elem
                        for j in range(i, (len(lista)-1)):
                            lista[j + 1] = temp[j]
                        lista.append(temp[len(temp)-1])
                        break        
    return lista


#Productores    

def p(almacen,poner,tomar, mutex):
    maximo = 0
    lista = []
    j = 0
    while j < N: #Generador de elementos aleatorios de forma creciente 
        n = random.randint(maximo,maximo + 100)
        lista.append(n)
        maximo = max(lista)
        j = j + 1
    lista.append(-1) #Añadimos el -1 al final
    print(lista)
    for v in lista:
        print (current_process().name, "está produciendo")
        time.sleep(random.random()/2)
        poner.acquire() #Semaforo que controla el acceso al buffer
        add_data(almacen, v, mutex)	
        print (current_process().name, "ha almacenado", v)
        tomar.release()   #Cada semaforo de los productores  
    

#Funcion que devuelve el minimo valor de los elementos positivos


def min_pos(almacen):
    aux = []
    for i in range(len(almacen)):
        if almacen[i] >= 0:
            aux.append(almacen[i])
    minimo = aux[0]
    for i in range(len(aux)):
        if (aux[i] < minimo):
            minimo = aux[i]
    return minimo

             
#Obtiene el minimo que haya en el almacen, lo elimina y lo inserta ordenadamente en la lista final


def get_data(almacen, mutex, final):
    mutex.acquire()
    try:
        data = min_pos(almacen)
        time.sleep(0.1)
        almacen.remove(data)
        final = insertar_ordenado(final, data)
        
    finally:
        mutex.release()
    return data
   

#Consumidores

def c(almacen,poner,tomar, mutex, final): 
    for v in range(N):
            tomar.acquire()        
            print (current_process().name, "está desalmacenando")
            data = get_data(almacen, mutex, final)
            poner.release()
            print (current_process().name, "ha consumido", data)
            time.sleep(random.random()/2)

            
 

     
         
#Funcion principal
 
if __name__ == "__main__":
    poner = BoundedSemaphore(K)  #Semaforo que controla el buffer
    tomar = BoundedSemaphore(K)  #Semaforo de cada uno de los productores que avisa cuando seguir produciendo
    mutex = Lock() #Semaforo binario que controla que no se mezclen los procesos de add_data y get_data
    for i in range(K): #Lista de semaforos de los productores
        tomar.acquire()

    manager = Manager()
    l = manager.list()
    final = manager.list()

    print ("almacen inicial", l[:])
    print ("lista inicial", final[:])
    
   
    procesos = []  #Lista de los productores
    consumidores = [] #Lista de los consumidores
    
    for i in range(K):
        procesos.append(Process(target = p, name = f'El Productor {i}', args = (l,poner,tomar,mutex)))
    for i in range(K):
        consumidores.append(Process(target = c, name = f'El Consumidor {i}', args = (l,poner,tomar,mutex,final)))
    
    for j in procesos + consumidores:
        j.start()
    for j in procesos + consumidores:
        j.join()
    
    print("almacen final", l[:])
    print("Lista final", final[:])
    print ("fin")