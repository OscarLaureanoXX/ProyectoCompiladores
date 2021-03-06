import sys
import re
from Structs import *

# Variables global
dir_func = 'None'
func_actual = 'global'
func_llamada = ''
var_actual = ['name','type']
oraculo = Semantic_Cube().cubo_semantico
cont_Temporales = 1
cont_Cuadruplos = 1
cont_Parametros = 0
cont_Read = 0
cont_Return = 0
cont_Special = 0
# Paquete de "memoria" para variables locales de funciones
# [int],[float],[bool],[string],[list]
paquetes = dict()
paquete_local = [[],[],[],[],[]]
first_go_to = False
apuntador_main = 0

# Memoria de ejecuccion
memoria = Execution_Memory()

# Valores de CODIGOS DE EJECUCCION
PRINT = '1'
SUMA = '2'
RESTA = '3'
MULTIPLICACION = '4'
DIVISION = '5'
MODULO = '6'
MAYOR = '7'
MENOR = '8'
MAYORIGUAL = '9'
MENORIGUAL = '10'
ASIGNACION = '11'
EQUAL = '12'
NOTEQUAL = '13'
GOTO = '14'
GOTOF = '15'
ENDPROC = '16'
ERA = '17'
PARAM = '18'
GOSUB = '19'
READ = '20'
ESPECIAL = '21'
RETURN = '22'
VER = '23'

# Pilas para expresiones
pilaOperandos = Stack()
pilaOperadores = Stack()
pilaTipos = Stack()
pilaSaltos = Stack()
pilaEspecial = Stack()

# Lista de cuadruplos
cuadruplos = list()

# Pilas para el for
pilaInicio = Stack()
pilaStep = Stack()



################################ TABLA DE FUNCIONES ################################################

# Inicializa el directorio de funciones y agrega la funcion global
def create_function_table():
  global dir_func
  dir_func = Dir_Func(dict())
  add_to_func_table('oscar', 'global')

# Agregar una funcion llamada [func_name] de tipo [func_type] 
# a la tabla de funciones [func_table]
def add_to_func_table(func_name, func_type):
  global func_actual
  global dir_func

  name = func_name.encode('UTF-8')
  tipo = func_type.encode('UTF-8')

  # Checando si ya existe esa funcion
  if func_name in dir_func.dictionary:
    print("Nombre de funcion repetido")
  else:
    # Agregar a la tabla de funciones
    # [tipo de la funcion, directorio de variables, firma, cantidad de variables locales, cuadruplo de inicio de la funcion]
    # la firma es un string que te dice cuantas variables de cada
    # tipo recibe como parametro 
    # orden = (i = int, f = float, s = string, b = bool, l = list)    
    dir_func.dictionary[name] = [tipo,{},'',0,-1]
    func_actual = name

# Actualizando la firma de la funcion (cuantas variables de cada tipo tiene)
# orden: (i = int, f = float, s = string, b = bool, l = list)
def update_func_firm():
  global dir_func
  global func_actual
  global var_actual

  # Obteniendo la firma de la funcion correspondiente
  firm = dir_func.dictionary[func_actual][2]

  # Actualizando la firma dependiendo del parametro nuevo
  # Y sacando el valor relativo de memoria de los argumentos
  if var_actual[1] == 'int':
    firm = firm + 'i'
  elif var_actual[1] == 'float':
    firm = firm + 'f'
  elif var_actual[1] == 'string':
    firm = firm + 's'
  elif var_actual[1] == 'bool':
    firm = firm + 'b'
  elif var_actual[1] == 'list':
    firm = firm + 'l'

  # Asignando el nuevo valor a la firma
  dir_func.dictionary[func_actual][2] = firm
  
  # Actualizando firma de funcion con las variables de parametro y su memoria relativa
  dir_func.dictionary[func_actual].append(var_actual[0])

# Sacar tipo y funcion para meter la variable a memoria
def crear_dir_memoria(func, tipo, var):
  global paquete_local
  # Variables globales
  if func == 'oscar':
    if tipo == 'int' and var not in memoria.globales[memoria.indexInt]:
      memoria.globales[memoria.indexInt].append(var)
      memoria.apuntador_globales_int += 1
    elif tipo == 'float' and var not in memoria.globales[memoria.indexFloat]:
      memoria.globales[memoria.indexFloat].append(var)
      memoria.apuntador_globales_float += 1
    elif tipo == 'bool' and var not in memoria.globales[memoria.indexBool]:
      memoria.globales[memoria.indexBool].append(var)
      memoria.apuntador_globales_bool += 1
    elif tipo == 'string' and var not in memoria.globales[memoria.indexString]:
      memoria.globales[memoria.indexString].append(var)
      memoria.apuntador_globales_string += 1
    elif tipo == 'list' and var not in memoria.globales[memoria.indexList]:
      memoria.globales[memoria.indexList].append(var)
      memoria.apuntador_globales_list += 1
  # Variables constantes
  elif func == 'constante':
    if tipo == 'int' and var not in memoria.constantes[memoria.indexInt]:
      memoria.constantes[memoria.indexInt].append(var)
      memoria.apuntador_constantes_int += 1
    elif tipo == 'float' and var not in memoria.constantes[memoria.indexFloat]:
      memoria.constantes[memoria.indexFloat].append(var)
      memoria.apuntador_constantes_float += 1
    elif tipo == 'bool' and var not in memoria.constantes[memoria.indexBool]:
      memoria.constantes[memoria.indexBool].append(var)
      memoria.apuntador_constantes_bool += 1
    elif tipo == 'string' and var not in memoria.constantes[memoria.indexString]:
      memoria.constantes[memoria.indexString].append(var)
      memoria.apuntador_constantes_string += 1
    elif tipo == 'list' and var not in memoria.constantes[memoria.indexList]:
      memoria.constantes[memoria.indexList].append(var)
      memoria.apuntador_constantes_list += 1
  else:
    if tipo == 'int' and var not in paquete_local[memoria.indexInt]:
      paquete_local[memoria.indexInt].append(var)
      memoria.apuntador_locales_int += 1
    elif tipo == 'float' and var not in paquete_local[memoria.indexFloat]:
      paquete_local[memoria.indexFloat].append(var)
      memoria.apuntador_locales_float += 1
    elif tipo == 'bool' and var not in paquete_local[memoria.indexBool]:
      paquete_local[memoria.indexBool].append(var)
      memoria.apuntador_locales_bool += 1
    elif tipo == 'string' and var not in paquete_local[memoria.indexString]:
      paquete_local[memoria.indexString].append(var)
      memoria.apuntador_locales_string += 1
    elif tipo == 'list' and var not in paquete_local[memoria.indexList]:
      paquete_local[memoria.indexList].append(var)
      memoria.apuntador_locales_list += 1


# Agregar una variable llamada [varName] de tipo [type] 
# a la tabla correspondiente
def add_to_var_table(varName, type):
  global dir_func
  global var_actual

  var = varName.encode('UTF-8')
  tipo = type.encode('UTF-8')
  # Checando si ya existe esa variable
  if var in dir_func.__getitem__(func_actual):
    print("Nombre de variable repetido")
  else:
    # Agregar a la tabla
    dir_func.__getitem__(func_actual)[var] = [tipo]
    # Contabilizando las variables locales
    dir_func.dictionary[func_actual][3] = dir_func.dictionary[func_actual][3] + 1

    # Meter a memoria la variable
    crear_dir_memoria(func_actual, tipo, var)

    # Manteniendo la variable actual y su tipo en un temporal para contabilizar despues
    var_actual[0] = var
    var_actual[1] = tipo

def set_func_start():
  global dir_func
  global cont_Cuadruplos
  global func_actual

  dir_func.dictionary[func_actual][4] = cont_Cuadruplos

def set_func_end():
  global cuadruplos
  global cont_Cuadruplos
  global cont_Temporales
  global memoria
  global paquete_local
  global paquetes
  global func_actual

  cuadruplo = Cuadruplo(cont_Cuadruplos, ENDPROC, '_', '_', '_')
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos = cont_Cuadruplos + 1

  # Reiniciando contadores de memoria
  paquetes[func_actual] = paquete_local
  paquete_local = [[],[],[],[],[]]

  cont_Temporales = 1

def create_packet_main():
  global paquete_local
  global paquetes

  # Reiniciando contadores de memoria
  paquetes[func_actual] = paquete_local
  paquete_local = [[],[],[],[],[]]

def create_return():
  global pilaOperandos
  global cont_Cuadruplos
  global cont_Return
  global cuadruplos

  value = pilaOperandos.pop()

  cuadruplo = Cuadruplo(cont_Cuadruplos, RETURN, value , '_', '_')
  cuadruplos.append(cuadruplo)
  
  cont_Return = cont_Cuadruplos
  cont_Cuadruplos = cont_Cuadruplos + 1

  
# Agregar numero de renglon de una lista [sizeR]
# a una tabla de variables con nombre [tableName]
def addRows(tableName, sizeR):
  global dir_func

  name = tableName.encode('UTF-8')
  rows = sizeR.encode('UTF-8')

  dir_func.__getitem__(func_actual)[name].append(rows)

# Agregar numero de columna de una lista [sizeC]
# a una tabla de variables con nombre [tableName]
def addColumns(tableName, sizeC):
  global dir_func
  
  name = tableName.encode('UTF-8')
  cols = sizeC.encode('UTF-8')

  dir_func.__getitem__(func_actual)[name].append(cols)

# Generar salto al main
def generate_first_goto():
  global cont_Cuadruplos
  global cuadruplos

  cuadruplo = Cuadruplo(cont_Cuadruplos, GOTO, '_', '_', '_')
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos += 1

def fill_first_goto():
  global cuadruplos
  global cont_Cuadruplos
  global first_go_to
  global apuntador_main

  for cuadruplo in cuadruplos:
    if cuadruplo['op'] ==  '14' and first_go_to == False:
      cuadruplo['res'] = str(cont_Cuadruplos)
      apuntador_main = str(cont_Cuadruplos)
      first_go_to = True

################################ /TABLA DE FUNCIONES ################################################

################################# LLAMADA A FUNCIONES ###############################################
def func_call_validation(func_name):
  global dir_func
  global cuadruplos
  global cont_Cuadruplos
  global func_llamada

  cont_Parametros = 0
  name = func_name.encode('UTF-8')

  # Validando que la funcion fue previamente declarada
  if name not in dir_func.dictionary:
    sys.exit("Funcion " + str(name) + " no declarada")
  
  # Generando el cuadruplo ERA de la funcion
  cuadruplo = Cuadruplo(cont_Cuadruplos, ERA, str(name), '_', '_')
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos += 1
  func_llamada = name

def func_add_argument():
  global pilaOperandos
  global pilaTipos
  global cont_Parametros
  global func_llamada
  global dir_func
  global cuadruplos
  global cont_Cuadruplos
  
  # Obteniendo el argumento y su tipo
  arg = pilaOperandos.pop()
  tipo = pilaTipos.pop()

  # Obteniendo la firma de la funcion
  firm = dir_func.dictionary[func_llamada][2]

  # Comparando el tipo del argumento contra la firma
  try:
    if tipo[0] != firm[cont_Parametros]:
      sys.exit("El parametro "+ str(cont_Parametros+1) + " de la funcion " + str(func_llamada) + " no es del tipo esperado ("+str(tipo)+")")
  except IndexError:
    sys.exit("Demasiados argumentos para la funcion")
  
  # Generando el cuadruplo del parametro
  cuadruplo = Cuadruplo(cont_Cuadruplos, PARAM, arg, tipo , str(cont_Parametros+1))
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos += 1
  cont_Parametros += 1

def func_gosub():
  global cuadruplos
  global cont_Cuadruplos
  global cont_Parametros
  global func_llamada
  global dir_func

  # Cuadruplo donde comienza la ejecucion de la funcion de la llamada
  initialCuad = dir_func.dictionary[func_llamada][4]

  # Reiniciando el contador de parametros
  cont_Parametros = 0

  # Generando el gosub
  cuadruplo = Cuadruplo(cont_Cuadruplos, GOSUB, str(func_llamada), '_', str(initialCuad))
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos += 1

def add_return_value(llamadaFuncion):
  global cont_Temporales
  global pilaOperandos
  global pilaTipos
  global func_actual

  nombreFuncion = llamadaFuncion.split('(')[0]
  tipoFuncion = dir_func.dictionary[nombreFuncion][0]
  
  pilaOperandos.push('return')
  pilaTipos.push(tipoFuncion)

################################# /LLAMADA A FUNCIONES ##############################################

######################################## LISTAS #####################################################
def nombre_arreglo():
  global pilaOperandos
  global pilaTipos
  global var_actual
  global memoria
  global paquete_local

  # Sacando la direccion de la variable
  direccionVar = int (pilaOperandos.peek())

  # Checando que la variable este en listas locales
  if direccionVar >= memoria.locales_list:
    # Buscando su nombre en la lista de locales
    var_actual = paquete_local[memoria.indexList][direccionVar - memoria.locales_list]
  # Checando si la variable esta en listas globales
  elif direccionVar >= 5000 and direccionVar < 6000:
    # Buscando su nombre en listas globales
    var_actual = memoria.globales[memoria.indexList][direccionVar - memoria.globales_list]
  else:
    print var_actual + " no es una variable dimensionada"


def verifica_index(dim):
  global pilaOperandos
  global pilaTipos
  global var_actual
  global cuadruplos
  global cont_Cuadruplos
  global dir_func
  global func_actual

  # Obteniendo las dimensiones de la variable
  # Buscando la variable en la tabla de variables local para sacar sus dimensiones
  if var_actual in dir_func.dictionary[func_actual][1]:
    limiteSup = int(dir_func.dictionary[func_actual][1][var_actual][dim])
  # Buscando la variable en la tabla de variables globales
  elif var_actual in dir_func.dictionary['oscar'][1]:
    limiteSup = int(dir_func.dictionary['oscar'][1][var_actual][dim])
  else:
    print var_actual + " no cuenta con dimensiones definidas"

  dimension = pilaOperandos.pop()


  # Generando el cuadruplo de verificar dimension
  cuadruplo = Cuadruplo(cont_Cuadruplos, VER, dimension, '0' , str(limiteSup-1))
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos += 1

listaTemporal = []
subListaTemporal = []

# Si el parametro es 1 hace una lista, si no hace una sublista
def crear_array(kind):
  global pilaOperandos
  global listaTemporal
  global subListaTemporal
  global memoria

  direccion = pilaOperandos.pop()
  valor = retornaValor(direccion)

  if kind == 1:
    listaTemporal.append(valor)
  else:
    subListaTemporal.append(valor)


def retornaValor(direccion):
  global memoria

  direccion = int (direccion)
  # Checando en memoria global
  if direccion >= memoria.globales_int and direccion < memoria.globales_float:
    return memoria.globales[memoria.indexInt][direccion-memoria.globales_int]
  elif direccion >= memoria.globales_float and direccion < memoria.globales_bool:
    return memoria.globales[memoria.indexFloat][direccion-memoria.globales_float]
  elif direccion >= memoria.globales_bool and direccion < memoria.globales_string:
    return memoria.globales[memoria.indexBool][direccion-memoria.globales_bool]
  elif direccion >= memoria.globales_string and direccion < memoria.globales_list:
    return memoria.globales[memoria.indexString][direccion-memoria.globales_string]
  elif direccion >= memoria.globales_list and direccion < memoria.constantes_int:
    return memoria.globales[memoria.indexList][direccion-memoria.globales_list]
  # Checando en memoria constante
  if direccion >= memoria.constantes_int and direccion < memoria.constantes_float:
    return memoria.constantes[memoria.indexInt][direccion-memoria.constantes_int]
  elif direccion >= memoria.constantes_float and direccion < memoria.constantes_bool:
    return memoria.constantes[memoria.indexFloat][direccion-memoria.constantes_float]
  elif direccion >= memoria.constantes_bool and direccion < memoria.constantes_string:
    return memoria.constantes[memoria.indexBool][direccion-memoria.constantes_bool]
  elif direccion >= memoria.constantes_string and direccion < memoria.constantes_list:
    return memoria.constantes[memoria.indexString][direccion-memoria.constantes_string]
  elif direccion >= memoria.constantes_list and direccion < memoria.locales_int:
    return memoria.constantes[memoria.indexList][direccion-memoria.constantes_list]
  # Checando en el paquete local
  if direccion >= memoria.locales_int and direccion < memoria.locales_float:
    return paquete_local[memoria.indexInt][direccion-memoria.locales_int]
  elif direccion >= memoria.locales_float and direccion < memoria.locales_bool:
    return paquete_local[memoria.indexFloat][direccion-memoria.locales_float]
  elif direccion >= memoria.locales_bool and direccion < memoria.locales_string:
    return paquete_local[memoria.indexBool][direccion-memoria.locales_bool]
  elif direccion >= memoria.locales_string and direccion < memoria.locales_list:
    return paquete_local[memoria.indexString][direccion-memoria.locales_string]
  elif direccion >= memoria.locales_list:
    return paquete_local[memoria.indexList][direccion-memoria.locales_list]

# Si el kind es 1 lo asigna como array final, si no lo hace como subarray
def asignar_array(kind):
  global listaTemporal
  global subListaTemporal
  global pilaOperandos
  global paquete_local

  if kind == 1:
    # Direccion de donde va a quedar
    direccion = len(paquete_local[memoria.indexList]) + memoria.locales_list

    # Asignar el arreglo al paquete en el lugar que le corresponde
    paquete_local[memoria.indexList].append(listaTemporal)

    # Agregando la direccion a la pila de operandos
    pilaOperandos.push(str(direccion))
    listaTemporal = []
  else:
    listaTemporal.append(subListaTemporal)
    subListaTemporal = []
  
  
  


  



######################################## /LISTAS ####################################################

# Agregar el operador [op] dentro de la pila de operadores
def add_to_operator_stack(op):
  global pilaOperadores
  
  #print("agregando operador" + op + " a la pila de operadores")
  pilaOperadores.push(op)

# Agregar la variable [id] dentro de la pila de operandos
def add_to_operand_stack(id, type):
  global pilaOperandos
  global pilaTipos
  global func_actual
  global dir_func

  id = id.encode('UTF-8')

  # Si es un int se agrega a la tabla de constante int
  if (type == 'int'):
      # .append(memoria.apuntador_locales_int)
    if id.isdigit():
      crear_dir_memoria('constante', type, id)
      id = str(dir_relativa('constante', type, id))
    else:
      if func_actual != 'oscar' and func_actual != 'main':
        dir_func.dictionary[func_actual][1][id].append(memoria.apuntador_locales_int)
      id = str(dir_relativa(func_actual, 'int', id))    

    pilaOperandos.push(id)
    pilaTipos.push('int')

  # Si es un float se agrega a la tabla de floats
  elif (type == 'float'):
    
    if re.match(r"^\d+?\.\d+?$", id):
      crear_dir_memoria('constante', type, id)
      id = str(dir_relativa('constante', type, id))
    else:
      if func_actual != 'oscar' and func_actual != 'main':
        dir_func.dictionary[func_actual][1][id].append(memoria.apuntador_locales_float)
      id = str(dir_relativa(func_actual, 'float', id))
    pilaOperandos.push(id)
    pilaTipos.push('float')
  
  # Si es un bool se agrega a la tabla de bools
  elif (type == 'bool'):
    if id[0] == '_':
      crear_dir_memoria('constante', type, id)
      id = str(dir_relativa('constante', type, id))
    else:
      if func_actual != 'oscar' and func_actual != 'main':
        dir_func.dictionary[func_actual][1][id].append(memoria.apuntador_locales_bool)
      id = str(dir_relativa(func_actual, 'bool', id))
    pilaOperandos.push(id)
    pilaTipos.push('bool')

  # Si es un string se agrega a la tabla de strings
  elif (type == 'string'):
    if id[0] == '"':
      crear_dir_memoria('constante', type, id)
      id = str(dir_relativa('constante', type, id))
    else:
      if func_actual != 'oscar' and func_actual != 'main':
        dir_func.dictionary[func_actual][1][id].append(memoria.apuntador_locales_string)
      id = str(dir_relativa(func_actual, 'string', id))
    pilaOperandos.push(id)
    pilaTipos.push('string')

  elif (type == 'list'):

    if id[0] == '[':
      crear_dir_memoria('constante', type, id)
      id = str(dir_relativa('constante', type, id))
    else:
      if func_actual != 'oscar' and func_actual != 'main':
        dir_func.dictionary[func_actual][1][id].append(memoria.apuntador_locales_list)
      id = str(dir_relativa(func_actual, 'list', id))

    pilaOperandos.push(id)
    pilaTipos.push('list')

  else:
    # buscar en la funcion actual, si no se encuentra entonces buscar en la funcion global
    try:
      tipo = dir_func.__getitem__(func_actual)[id][0]
      # Intentar sacar valor relativo de memoria
      try:
        id = str(dir_relativa(func_actual, tipo, id))
      # Si no lo encuentra, buscar en la firma de la funcion
      except IndexError:
        index = dir_func.dictionary[func_actual][5:].index(id)
        id = str(dir_func.dictionary[func_actual][index+5])
    except KeyError:
      # Si no se encuentra en la funcion global entonces marcar error
      try:
        tipo = dir_func.__getitem__('oscar')[id][0]
        id = str(dir_relativa('oscar', tipo, id))
      except KeyError:
        sys.exit("Variable " + "'" + id + "'" + " no declarada")
        return
    pilaOperandos.push(id)
    pilaTipos.push(tipo)

# Funcion que retorna el valor de la direccion relativa de memoria de la variable
def dir_relativa(func, tipo, id):
  global paquete_local
  # Buscar si es global
  if func == 'oscar':
    # Checar el tipo
    if tipo == 'int' and id in memoria.globales[memoria.indexInt]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.globales[memoria.indexInt].index(id)
      return index + memoria.globales_int
      # Retornar valor memoria
    elif tipo == 'float' and id in memoria.globales[memoria.indexFloat]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.globales[memoria.indexFloat].index(id)
      return index + memoria.globales_float
    elif tipo == 'bool' and id in memoria.globales[memoria.indexBool]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.globales[memoria.indexBool].index(id)
      return index + memoria.globales_bool
    elif tipo == 'string' and id in memoria.globales[memoria.indexString]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.globales[memoria.indexString].index(id)
      return index + memoria.globales_string
    elif tipo == 'list' and id in memoria.globales[memoria.indexList]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.globales[memoria.indexList].index(id)
      return index + memoria.globales_list
  # Si el valor es una constante
  elif func == 'constante':
    if tipo == 'int' and id in memoria.constantes[memoria.indexInt]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.constantes[memoria.indexInt].index(id)
      return index + memoria.constantes_int
    elif tipo == 'float' and id in memoria.constantes[memoria.indexFloat]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.constantes[memoria.indexFloat].index(id)
      return index + memoria.constantes_float
    elif tipo == 'bool' and id in memoria.constantes[memoria.indexBool]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.constantes[memoria.indexBool].index(id)
      return index + memoria.constantes_bool
    elif tipo == 'string' and id in memoria.constantes[memoria.indexString]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.constantes[memoria.indexString].index(id)
      return index + memoria.constantes_string
    elif tipo == 'list' and id in memoria.constantes[memoria.indexList]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = memoria.constantes[memoria.indexList].index(id)
      return index + memoria.constantes_list
  else:
    # Checar su tipo
    if tipo == 'int' and id in paquete_local[memoria.indexInt]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = paquete_local[memoria.indexInt].index(id)
      return index + memoria.locales_int
    elif tipo == 'float' and id in paquete_local[memoria.indexFloat]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = paquete_local[memoria.indexFloat].index(id)
      return index + memoria.locales_float
    elif tipo == 'bool' and id in paquete_local[memoria.indexBool]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = paquete_local[memoria.indexBool].index(id)
      return index + memoria.locales_bool
    elif tipo == 'string' and id in paquete_local[memoria.indexString]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = paquete_local[memoria.indexString].index(id)
      return index + memoria.locales_string
    elif tipo == 'list' and id in paquete_local[memoria.indexList]:
      # Si el valor ya esta en memoria
      # Retornar su valor de memoria
      index = paquete_local[memoria.indexList].index(id)
      return index + memoria.locales_list
    
def pop_sum_from_stack():
  global pilaOperandos
  global pilaTipos
  global pilaOperadores
  global cont_Temporales
  global func_actual

  suma = pilaOperadores.pop()
  der = pilaOperandos.pop()
  t1 = pilaTipos.pop()
  izq = pilaOperandos.pop()
  t2 = pilaTipos.pop()
  temp = 't'+ str(cont_Temporales)

  tipoRes = oraculo[t1][t2][suma]
  crear_dir_memoria(func_actual, tipoRes, temp)

  if (tipoRes == 'ERR'):
    print t1," ",t2
    sys.exit('Tipos compatibles para la operacion ' + suma)

  temp = str(dir_relativa(func_actual, tipoRes, temp))

  pilaOperandos.push(temp)

  # Impresion de Cuadruplos
  global cont_Cuadruplos
  global cuadruplos
  if (suma == '+'):
    cuadruplo = Cuadruplo(cont_Cuadruplos, SUMA, izq, der, temp)
  else:
    cuadruplo = Cuadruplo(cont_Cuadruplos, RESTA, izq, der, temp)
  cuadruplos.append(cuadruplo)
  
  
  pilaTipos.push(tipoRes)
  cont_Temporales += 1
  cont_Cuadruplos += 1

def pop_mult_from_stack():
  global pilaOperandos
  global pilaTipos
  global pilaOperadores
  global cont_Temporales

  mult = pilaOperadores.pop()
  der = pilaOperandos.pop()
  t1 = pilaTipos.pop()
  izq = pilaOperandos.pop()
  t2 = pilaTipos.pop()
  temp = 't'+ str(cont_Temporales)

  tipoRes = oraculo[t1][t2][mult]
  crear_dir_memoria(func_actual, tipoRes, temp)

  if (tipoRes == 'ERR'):
    sys.exit('Tipos compatibles para la operacion ' + mult)

  temp = str(dir_relativa(func_actual, tipoRes, temp))

  pilaOperandos.push(temp)

  # Impresion de Cuadruplos
  global cont_Cuadruplos
  global cuadruplos
  if (mult == '*'):
    cuadruplo = Cuadruplo(cont_Cuadruplos, MULTIPLICACION, izq, der, temp)
  elif (mult == '/'):
    cuadruplo = Cuadruplo(cont_Cuadruplos, DIVISION, izq, der, temp)
  else:
    cuadruplo = Cuadruplo(cont_Cuadruplos, MODULO, izq, der, temp)
  cuadruplos.append(cuadruplo)

  pilaTipos.push(tipoRes)
  cont_Temporales += 1
  cont_Cuadruplos += 1

def pop_equals_from_stack():
  global pilaOperandos
  global pilaTipos
  global pilaOperadores
  global cuadruplos

  igual = pilaOperadores.pop()
  der = pilaOperandos.pop()
  t1 = pilaTipos.pop()
  izq = pilaOperandos.pop()
  t2 = pilaTipos.pop()



  if(t1 == t2) or True:
    global cont_Cuadruplos
    global cuadruplos
    global cont_Return
    global cont_Special

    if (der == 'read'):
      for cuadruplo in cuadruplos:
        if int(cuadruplo['cont']) == cont_Read:
          cuadruplo['res'] = str(cont_Cuadruplos)
    
    if (der == 'return'):
      for cuadruplo in cuadruplos:
        if int(cuadruplo['cont']) == cont_Return:
          cuadruplo['res'] = str(cont_Cuadruplos)

    if (der == 'special'):
      for cuadruplo in cuadruplos:
        if int(cuadruplo['cont']) == cont_Special:
          cuadruplo['res'] = str(cont_Cuadruplos)

  
    cuadruplo = Cuadruplo(cont_Cuadruplos , ASIGNACION, der, '_', izq)
    cont_Cuadruplos += 1
    cuadruplos.append(cuadruplo)
    pilaTipos.push(t1)
  # else:
  #   pilaTipos.display()
  #   print t1," ",t2
  #   sys.exit("Incompatible type for operation " + igual)
  

def pop_rel_from_stack():
  global pilaOperandos
  global pilaTipos
  global pilaOperadores
  global cont_Temporales

  rel = pilaOperadores.pop()
  der = pilaOperandos.pop()
  t1 = pilaTipos.pop()
  izq = pilaOperandos.pop()
  t2 = pilaTipos.pop()
  temp = 't'+ str(cont_Temporales)

  tipoRes = oraculo[t1][t2][rel]
  crear_dir_memoria(func_actual, tipoRes, temp)

  if (tipoRes == 'ERR'):
    sys.exit('Tipos compatibles para la operacion ' + rel)

  temp = str(dir_relativa(func_actual, tipoRes, temp))

  pilaOperandos.push(temp)

  # Impresion de Cuadruplos
  global cont_Cuadruplos
  global cuadruplos
  if (rel == '>'):
    cuadruplo = Cuadruplo(cont_Cuadruplos, MAYOR, izq, der, temp)
  elif (rel == '<'):
    cuadruplo = Cuadruplo(cont_Cuadruplos, MENOR, izq, der, temp)
  elif (rel == '<='):
    cuadruplo = Cuadruplo(cont_Cuadruplos, MENORIGUAL, izq, der, temp)
  elif (rel == '>='):
    cuadruplo = Cuadruplo(cont_Cuadruplos, MAYORIGUAL, izq, der, temp)
  elif (rel == '=='):
    cuadruplo = Cuadruplo(cont_Cuadruplos, EQUAL, izq, der, temp)
  else:
    cuadruplo = Cuadruplo(cont_Cuadruplos, NOTEQUAL, izq, der, temp)
  cuadruplos.append(cuadruplo)

  pilaTipos.push(tipoRes)
  cont_Temporales += 1
  cont_Cuadruplos += 1

########################## CONDICIONALES ############################

def add_conditional():
  global cont_Cuadruplos
  global cuadruplos
  global pilaOperandos
  global pilaSaltos
  global pilaTipos

  # Validando que la expresion del if sea bool
  if pilaTipos.peek() != 'bool':
    sys.exit("Error: Expected bool expresion inside if(expresion)")
  
  # Obteniendo el resultado de la expresion para el cuadruplo
  res_Expresion = pilaOperandos.peek()

  # Generando cuadruplo con GOTOF (go to en false)
  cuadruplo = Cuadruplo(cont_Cuadruplos, GOTOF,res_Expresion,'_','_')

  # Metiendo el cuadruplo
  cuadruplos.append(cuadruplo)
  # Agregando la linea a la pila de saltos
  pilaSaltos.push(cont_Cuadruplos)

  cont_Cuadruplos += 1

def add_else():
  global cont_Cuadruplos
  global cuadruplos
  global pilaSaltos

  # Generar cuadruplo para saltar el else
  cuadruplo = Cuadruplo(cont_Cuadruplos, GOTO,'_','_','_')
  cuadruplos.append(cuadruplo)

  # Llenando el GOTOF del if correspondiente
  fill = pilaSaltos.pop()
  pilaSaltos.push(cont_Cuadruplos)

  cuadruplos.__getitem__(fill-1)['res'] = str(cont_Cuadruplos + 1)

  cont_Cuadruplos += 1

def add_end_conditional():
  global cont_Cuadruplos
  global cuadruplos
  global pilaSaltos

  # Llenando el cuadruplo final correspondiente
  final = pilaSaltos.pop()
  cuadruplos.__getitem__(final-1)['res'] = str(cont_Cuadruplos)

########################## /CONDICIONALES ############################

############################### WHILE ################################
def add_while():
  global pilaSaltos
  global cont_Cuadruplos

  pilaSaltos.push(cont_Cuadruplos)

def add_expr_while():
  add_conditional()

def add_end_while():
  global pilaSaltos
  global cont_Cuadruplos

  fin = pilaSaltos.pop()
  ret = str(pilaSaltos.pop())

  # Generar cuadruplo para volver a evaluar el while
  cuadruplo = Cuadruplo(cont_Cuadruplos, GOTO,'_','_', ret)
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos += 1

  # Llenando el cuadruplo final correspondiente
  cuadruplos.__getitem__(fin-1)['res'] = str(cont_Cuadruplos)

############################### /WHILE ###############################

################################# FOR ################################
def add_for_inicio(id):
  global pilaTipos
  global pilaOperandos
  global pilaInicio
  global func_actual

  # Validando que la expresion del inicio del for sea int
  if pilaTipos.peek() != 'int':
    sys.exit("Error: Expected int expresion on first parameter (START) of for")

  # Metiendo el inicio del for
  id = id.encode('UTF-8')
  id = str(dir_relativa(func_actual, 'int', id))
  pilaInicio.push(id)

def add_for_limite():
  global pilaOperandos
  global pilaTipos
  global pilaStep
  global cont_Cuadruplos
  global cuadruplos
  global cont_Temporales

  # Validando que la expresion del limite superior sea int
  if pilaTipos.peek() != 'int':
    sys.exit("Error: Expected int expresion on second parameter (MAX) of for")

  # Obteniendo inicio y limite superior del ciclo
  inicio = pilaInicio.peek()
  lim_superior = pilaOperandos.peek()

  # Metiendo migaja de pan
  pilaSaltos.push(cont_Cuadruplos)

  # Generar cuadruplo de comparacion
  temp = 't'+ str(cont_Temporales)
  crear_dir_memoria(func_actual, 'bool', temp)
  temp = str(dir_relativa(func_actual, 'bool', temp))

  cuadruplo = Cuadruplo(cont_Cuadruplos, MENORIGUAL , inicio , lim_superior , temp)
  cuadruplos.append(cuadruplo)

  cont_Temporales = cont_Temporales + 1
  cont_Cuadruplos = cont_Cuadruplos + 1

  # Generar cuadruplo de gotof
  cuadruplo = Cuadruplo(cont_Cuadruplos, GOTOF , temp , '_', '_')
  cuadruplos.append(cuadruplo)
  cont_Cuadruplos = cont_Cuadruplos + 1

  # Metiendo a la pila de Steps el valor por default del for (1)
  if '1' not in memoria.constantes:
    crear_dir_memoria('constante', 'int', '1')
  step = str(dir_relativa('constante', 'int', '1'))
  pilaStep.push(step)

  # Metiendo migaja de pan
  pilaSaltos.push(cont_Cuadruplos)

def add_for_step():
  global pilaTipos
  global pilaOperandos
  global pilaStep

  # Validando que la expresion del los saltos sea int
  if pilaTipos.peek() != 'int':
    sys.exit("Error: Expected int expresion on third parameter (STEP) of for")
  
  # Sacar el 1 de step default para vaciar la pila
  pilaStep.pop()
  step = pilaOperandos.peek()
  pilaStep.push(step)

def add_for_final():
  global cont_Cuadruplos
  global cuadruplos
  global cont_Temporales
  global pilaStep
  global pilaInicio
  global pilaTipos

  # Variables para los cuadruplos
  inicio = pilaInicio.pop()
  step = pilaStep.pop()
  fin = pilaSaltos.pop()
  ret = pilaSaltos.pop()

  # Generar cuadruplos de aumento de la variable controladora
  temp = 't'+ str(cont_Temporales)
  crear_dir_memoria(func_actual, 'int', temp)
  temp = str(dir_relativa(func_actual, 'int', temp))

  cuadruplo = Cuadruplo(cont_Cuadruplos, SUMA , inicio , step , temp)
  cuadruplos.append(cuadruplo)

  cont_Temporales = cont_Temporales + 1
  cont_Cuadruplos = cont_Cuadruplos + 1

  cuadruplo = Cuadruplo(cont_Cuadruplos, ASIGNACION , temp , '_' , inicio)
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos = cont_Cuadruplos + 1

  # Generar cuadruplo para volver a evaluar

  cuadruplo = Cuadruplo(cont_Cuadruplos, GOTO , '_' , '_' , str(ret))
  cuadruplos.append(cuadruplo)

  cont_Cuadruplos = cont_Cuadruplos + 1

  # Llenando el cuadruplo del gotoF pendiente
  cuadruplos.__getitem__(fin-2)['res'] = str(cont_Cuadruplos)

################################ /FOR ################################

def add_print():
  global pilaOperandos
  global pilaTipos
  global cont_Cuadruplos
  global cuadruplos

  printeado = pilaOperandos.peek()
  cuadruplo = Cuadruplo(cont_Cuadruplos , PRINT, '_', '_', printeado)

  cuadruplos.append(cuadruplo)
  cont_Cuadruplos += 1

def generate_read(tipo):
  global cont_Cuadruplos
  global cuadruplos
  global pilaOperandos
  global pilaTipos
  global cont_Read

  tipo = tipo.encode("UTF-8")

  pilaOperandos.push('read')
  pilaTipos.push(tipo)

  cuadruplo = Cuadruplo(cont_Cuadruplos, READ, tipo, '_', '_')
  cuadruplos.append(cuadruplo)
  cont_Read = cont_Cuadruplos
  cont_Cuadruplos += 1

def add_special(type):
  global pilaOperandos
  global pilaTipos
  global cont_Special

  pilaOperandos.push('special')
  pilaTipos.push(type)
  cont_Special = cont_Cuadruplos - 1

# Generar cuadruplos para funciones especiales de un parametro
def generate_special_function(function, id):
  global cont_Cuadruplos
  global cuadruplos
  global pilaOperandos
  global pilaTipos
  global paquete_local

  id = id.encode('UTF-8')
  if id[0] == '"':
    id = str(dir_relativa('oscar', 'string', id))
  else:
    id = str(dir_relativa('oscar', 'list', id))

  cuadruplo = Cuadruplo(cont_Cuadruplos, ESPECIAL, function, id , '_')
  cuadruplos.append(cuadruplo)
  cont_Cuadruplos += 1

# Agregar parametros de funciones especiales dentro de la pila de especiales para poder despues armar el paquete de parametros
def add_special_stack(id, tipo):
  global pilaEspecial

  id = id.encode('UTF-8')
  tipo = tipo.encode('UTF-8')

  pilaEspecial.push(id)
  pilaEspecial.push(tipo)

# Generar cuadruplos para funciones especiales de 2 argumentos 
def generate_special_function2(function):
  global pilaEspecial
  global cont_Cuadruplos
  global cuadruplos

  tipoParam1 = pilaEspecial.pop()
  param1 = pilaEspecial.pop()
  if param1.isdigit():
    param1 = str(dir_relativa('constante', tipoParam1, param1)) 
  else: 
    param1 = str(dir_relativa('oscar', tipoParam1, param1))

  tipoParam2 = pilaEspecial.pop()
  param2 = pilaEspecial.pop()
  param2 = str(dir_relativa('oscar', tipoParam2, param2))

  paquete_params = [param1, param2]

  cuadruplo = Cuadruplo(cont_Cuadruplos, ESPECIAL, function, str(paquete_params), '_')
  cuadruplos.append(cuadruplo)
  cont_Cuadruplos += 1

# Generar cuadruplos para funciones especiales de 3 argumentos 
def generate_special_function3(function):
  global pilaEspecial
  global cont_Cuadruplos
  global cuadruplos

  tipoParam1 = pilaEspecial.pop()
  param1 = pilaEspecial.pop()
  if param1.isdigit():
    param1 = str(dir_relativa('constante', tipoParam1, param1)) 
  else: 
    param1 = str(dir_relativa('oscar', tipoParam1, param1))

  tipoParam2 = pilaEspecial.pop()
  param2 = pilaEspecial.pop()
  if param2.isdigit():
    param2 = str(dir_relativa('constante', tipoParam2, param2)) 
  else: 
    param2 = str(dir_relativa('oscar', tipoParam2, param2))

  tipoParam3 = pilaEspecial.pop()
  param3 = pilaEspecial.pop()
  if param3.isdigit():
    param3 = str(dir_relativa('constante', tipoParam3, param3)) 
  else: 
    param3 = str(dir_relativa('oscar', tipoParam3, param3))

  paquete_params = [param1, param2, param3]

  cuadruplo = Cuadruplo(cont_Cuadruplos, ESPECIAL, function, str(paquete_params), '_')
  cuadruplos.append(cuadruplo)
  cont_Cuadruplos += 1



def destroy():
  global paquetes
  # Imprimiendo toda la tabla
  # print(dir_func.dictionary)
  for i in cuadruplos:
    print(i)
  # print(paquetes)
  # print apuntador_main