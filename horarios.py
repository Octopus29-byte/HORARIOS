import random
from collections import defaultdict

# Parámetros del sistema
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
HORARIOS = ["8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"]
RECESO = "Receso"
DURACION_CLASE = 6

# Configuración de materias con horas semanales 
MATERIAS = {
    "Matemáticas": 12,
    "Física": 12,
    "Química": 12,
    "Historia": 12,
    "Literatura": 12
}

RESTRICCIONES_AULAS = {
    "Química": {"Aula 101", "Aula 102"}, 
    "Física": {"Aula 105"},              
}

PROFESORES = ["Prof. A",
              "Prof. B",
              "Prof. C",
              "Prof. D",
              "Prof. E"]

AULAS = ["Aula 101",
         "Aula 102",
         "Aula 103",
         "Aula 104",
         "Aula 105"]


# Parámetros del algoritmo genético
TAM_POBLACION = 300
NUM_GENERACIONES = 10000
PROB_MUTACION = 0.5
TAM_TORNEO = 5

class Horario:
    def __init__(self, clases=None, profesores=None, aulas=None):
        self.clases = clases if clases else []
        self.profesores = profesores if profesores else PROFESORES
        self.aulas = aulas if aulas else AULAS
        self._fitness = None


################################################ GENERACIÓN #############################################################

    def generar_aleatorio(self):
            """Genera horarios válidos garantizando 5 horas exactas por materia"""
            self.clases = []
            intentos_maximos = 5000
            intentos = 0

            while intentos < intentos_maximos:
                try:
                    # Reiniciamos estructuras de control
                    ocupacion = {dia: {'horas': set(), 'profesores': set(), 'aulas': set(), 'materias': set()} for dia in DIAS}
                    materias_asignadas = {materia: 0 for materia in MATERIAS}

                    # Asignamos TODAS las materias primero
                    for materia in MATERIAS:
                        sesiones_asignadas = 0
                        while materias_asignadas[materia] < MATERIAS[materia] and intentos < intentos_maximos:
                            intentos += 1
                            dia = random.choice(DIAS)

                            # Evitar repetir materia en el mismo día
                            if materia in ocupacion[dia]['materias']:
                                continue

                            # Seleccionar profesor y aula
                            profesor = random.choice(self.profesores)
                            aula = random.choice(self.aulas)

                            # Buscar horario disponible para 2.5 hrs (5 bloques)
                            horarios_disponibles = [
                                h for h in HORARIOS
                                if h not in ocupacion[dia]['horas'] and
                                HORARIOS.index(h) + DURACION_CLASE <= len(HORARIOS)
                            ]

                            if not horarios_disponibles:
                                continue

                            inicio = random.choice(horarios_disponibles)
                            idx = HORARIOS.index(inicio)
                            horas_bloque = HORARIOS[idx:idx+DURACION_CLASE]

                            # Verificar disponibilidad de profesor y aula
                            if (any(h in ocupacion[dia]['profesores'] for h in horas_bloque)) or \
                              (any(h in ocupacion[dia]['aulas'] for h in horas_bloque)):
                                continue

                            # Asignar la clase
                            fin = HORARIOS[idx+DURACION_CLASE-1]
                            self.clases.append((dia, f"{inicio} - {fin}", materia, profesor, aula))

                            # Actualizar estructuras de control
                            ocupacion[dia]['horas'].update(horas_bloque)
                            ocupacion[dia]['profesores'].update(horas_bloque)
                            ocupacion[dia]['aulas'].update(horas_bloque)
                            ocupacion[dia]['materias'].add(materia)
                            materias_asignadas[materia] += DURACION_CLASE

                    # Verificar que todas las materias tengan sus horas completas
                    if all(v == MATERIAS[materia] for materia, v in materias_asignadas.items()):
                        # Asignar recesos según las reglas
                        self.asignar_recesos(ocupacion)
                        return self

                except Exception as e:
                    print(f"Error durante generación: {e}")
                    continue

            raise Exception("No se pudo generar un horario válido después de {} intentos".format(intentos_maximos))


  #=========================================================================================================#


    def generar_dia_aleatorio(self, dia=None):
          """Genera clases aleatorias para un día específico o para materias faltantes"""
          # Calcular horas faltantes por materia
          horas_materia = defaultdict(int)
          for clase in self.clases:
              if clase[2] in MATERIAS:
                  duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
                  horas_materia[clase[2]] += duracion

          materias_faltantes = [m for m in MATERIAS if horas_materia[m] < MATERIAS[m]]

          if not materias_faltantes:
              return

          # Seleccionar día si no se especificó
          if dia is None:
              dias_disponibles = [d for d in DIAS if len([c for c in self.clases if c[0] == d]) < 4]  # Máximo 4 clases por día
              if not dias_disponibles:
                  return
              dia = random.choice(dias_disponibles)

          # Verificar que la materia no esté ya en ese día
          materias_dia = {c[2] for c in self.clases if c[0] == dia}
          materias_posibles = [m for m in materias_faltantes if m not in materias_dia]

          if not materias_posibles:
              return

          materia = random.choice(materias_posibles)
          profesor = random.choice(self.profesores)
          aula = random.choice(self.aulas)

          # Encontrar slot disponible
          ocupacion = {h: False for h in HORARIOS}
          for c in self.clases:
              if c[0] == dia:
                  inicio, fin = c[1].split(" - ")
                  for h in HORARIOS[HORARIOS.index(inicio):HORARIOS.index(fin)+1]:
                      ocupacion[h] = True

          # Buscar slots consecutivos disponibles
          slots_disponibles = []
          for i in range(len(HORARIOS) - DURACION_CLASE + 1):
              if all(not ocupacion[HORARIOS[j]] for j in range(i, i + DURACION_CLASE)):
                  slots_disponibles.append(HORARIOS[i])

          if slots_disponibles:
              inicio = random.choice(slots_disponibles)
              fin = HORARIOS[HORARIOS.index(inicio) + DURACION_CLASE - 1]
              self.clases.append((dia, f"{inicio} - {fin}", materia, profesor, aula))
              return True
          return False

########################################### REPARACIÓN/OPTIMIZACIÓN ########################################################

    def asignar_recesos(self, ocupacion):
      """Asigna recesos cumpliendo estrictamente las reglas especificadas"""
      for dia in DIAS:
          # Calcular horas lectivas y recesos existentes
          clases_dia = [c for c in self.clases if c[0] == dia]
          horas_clase = sum(
              (HORARIOS.index(c[1].split(" - ")[1]) - HORARIOS.index(c[1].split(" - ")[0]) + 1) * 0.5
              for c in clases_dia if c[2] in MATERIAS
          )
          recesos_existentes = [c for c in clases_dia if c[2] == RECESO]

          # Determinar recesos necesarios (según tus reglas exactas)
          if horas_clase <= 3:
              recesos_necesarios = 0
          elif 3 < horas_clase <= 6:
              recesos_necesarios = 1
          elif 6 < horas_clase <= 9:
              recesos_necesarios = 2
          else:
              recesos_necesarios = 3

          # Eliminar todos los recesos existentes del día (los reasignaremos)
          self.clases = [c for c in self.clases if not (c[0] == dia and c[2] == RECESO)]

          # Reordenar clases del día
          clases_dia = sorted(
              [c for c in self.clases if c[0] == dia],
              key=lambda x: HORARIOS.index(x[1].split(" - ")[0]))

          # Solo asignar recesos si hay clases
          if not clases_dia:
              continue

          # Lista para nuevos recesos
          nuevos_recesos = []

          huecos_validos = []
          for i in range(len(clases_dia)-1):
              fin_clase = HORARIOS.index(clases_dia[i][1].split(" - ")[1])
              inicio_sig = HORARIOS.index(clases_dia[i+1][1].split(" - ")[0])

              # Hueco válido debe tener al menos 1 bloque (30 min) y no estar al inicio/final
              if inicio_sig > fin_clase:
                  huecos_validos.append({
                      'posicion': fin_clase,
                      'duracion': inicio_sig - fin_clase,
                      'entre_clases': (i, i+1)
                  })

          # Ordenar huecos por duración (mayores primero)
          huecos_validos.sort(key=lambda x: -x['duracion'])

          # Asignar recesos necesarios en los mejores huecos
          for i in range(min(recesos_necesarios, len(huecos_validos))):
              hueco = huecos_validos[i]
              pos = hueco['posicion']

              # Asegurar que no creamos recesos consecutivos
              if (i > 0 and huecos_validos[i-1]['posicion'] == pos - 1):
                  continue  # Saltar para evitar recesos adyacentes

              nuevos_recesos.append((
                  dia,
                  f"{HORARIOS[pos]} - {HORARIOS[pos+1]}",
                  RECESO,
                  "-",
                  "-"
              ))

          # Agregar los nuevos recesos al horario
          self.clases.extend(nuevos_recesos)

          # Reordenar todo el día
          self.clases.sort(key=lambda x: (DIAS.index(x[0]), HORARIOS.index(x[1].split(" - ")[0])))

    #=========================================================================================================#

    def reparar_horario(self):
          """Repara el horario completando días y materias faltantes"""
          # 1. Eliminar asignaciones excedentes
          horas_materia = defaultdict(int)
          clases_validas = []

          for clase in self.clases:
              if clase[2] in MATERIAS:
                  duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
                  if horas_materia[clase[2]] + duracion <= MATERIAS[clase[2]]:
                      clases_validas.append(clase)
                      horas_materia[clase[2]] += duracion
              else:
                  clases_validas.append(clase)  # Mantener recesos

          self.clases = clases_validas

          # 2. Completar días faltantes
          dias_presentes = {c[0] for c in self.clases}
          for dia in DIAS:
              if dia not in dias_presentes:
                  for _ in range(3):  # Intentar 3 veces
                      if self.generar_dia_aleatorio(dia):
                          break

          # 3. Completar materias faltantes
          for _ in range(20):  # Intentar completar materias 20 veces
              if not any(self.generar_dia_aleatorio() for _ in range(5)):
                  break

          # 4. Reasignar recesos
          ocupacion = {dia: {'horas': set(), 'profesores': set(), 'aulas': set(), 'materias': set()} for dia in DIAS}
          for clase in self.clases:
              dia = clase[0]
              inicio, fin = clase[1].split(" - ")
              horas = HORARIOS[HORARIOS.index(inicio):HORARIOS.index(fin)+1]
              ocupacion[dia]['horas'].update(horas)
              if clase[2] in MATERIAS:
                  ocupacion[dia]['profesores'].update(horas)
                  ocupacion[dia]['aulas'].update(horas)
                  ocupacion[dia]['materias'].add(clase[2])

          # Fuerza la verificación de recesos
          ocupacion = {dia: {'horas': set()} for dia in DIAS}
          for c in self.clases:
              if c[2] != RECESO:
                  dia = c[0]
                  inicio, fin = c[1].split(" - ")
                  horas = range(HORARIOS.index(inicio), HORARIOS.index(fin)+1)
                  ocupacion[dia]['horas'].update(horas)

          self.asignar_recesos(ocupacion)

########################################### OPERACIONES GENÉTICAS ########################################################

    def cruzar_dias_avanzado(self, otro_horario):
          """
          Cruza dos horarios intercambiando bloques de días distintos,
          asegurando que no se dupliquen materias en los hijos.
          Retorna dos nuevos horarios hijos.
          """
          # Seleccionar días únicos para intercambiar (sin repetir entre padres)
          dias_disponibles = DIAS.copy()
          random.shuffle(dias_disponibles)

          # Dividir días en dos grupos (para hijo1 y hijo2)
          split_point = random.randint(1, 4)  # Al menos 1 día y máximo 4
          dias_padre1 = dias_disponibles[:split_point]
          dias_padre2 = dias_disponibles[split_point:]

          # Construir hijos combinando los días seleccionados
          clases_hijo1 = []
          clases_hijo2 = []

          # Diccionarios para verificar horas semanales por materia
          horas_hijo1 = defaultdict(int)
          horas_hijo2 = defaultdict(int)

          # Procesar días del padre1 para hijo1
          for dia in dias_padre1:
              for clase in self.clases:
                  if clase[0] == dia:
                      materia = clase[2]
                      if materia in MATERIAS:
                          duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
                          if horas_hijo1[materia] + duracion <= MATERIAS[materia]:
                              clases_hijo1.append(clase)
                              horas_hijo1[materia] += duracion

          # Procesar días del padre2 para hijo1 (complemento)
          for dia in dias_padre2:
              for clase in otro_horario.clases:
                  if clase[0] == dia:
                      materia = clase[2]
                      if materia in MATERIAS:
                          duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
                          if horas_hijo1[materia] + duracion <= MATERIAS[materia]:
                              clases_hijo1.append(clase)
                              horas_hijo1[materia] += duracion

          # Repetir lógica para hijo2 (invertiendo padres)
          for dia in dias_padre2:
              for clase in self.clases:
                  if clase[0] == dia:
                      materia = clase[2]
                      if materia in MATERIAS:
                          duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
                          if horas_hijo2[materia] + duracion <= MATERIAS[materia]:
                              clases_hijo2.append(clase)
                              horas_hijo2[materia] += duracion

          for dia in dias_padre1:
              for clase in otro_horario.clases:
                  if clase[0] == dia:
                      materia = clase[2]
                      if materia in MATERIAS:
                          duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
                          if horas_hijo2[materia] + duracion <= MATERIAS[materia]:
                              clases_hijo2.append(clase)
                              horas_hijo2[materia] += duracion

          return Horario(clases_hijo1), Horario(clases_hijo2)


     #=========================================================================================================#

    def mutar(self):
            """Versión mejorada del operador de mutación"""
            if not self.clases:
                return self

            # 1. Seleccionar clase a mutar (no receso)
            clases_validas = [c for c in self.clases if c[2] in MATERIAS]
            if not clases_validas:
                return self

            clase = random.choice(clases_validas)
            self.clases.remove(clase)

            # 2. Intentar recolocación 
            for _ in range(50):  
                nuevo_dia = random.choice(DIAS)

                # Verificar que la materia no se repita ese día
                if any(c[0] == nuevo_dia and c[2] == clase[2] for c in self.clases):
                    continue

                # Calcular ocupación del día
                ocupacion = {
                    'horas': set(),
                    'profesores': set(),
                    'aulas': set()
                }
                for c in self.clases:
                    if c[0] == nuevo_dia:
                        inicio, fin = c[1].split(" - ")
                        horas = HORARIOS[HORARIOS.index(inicio):HORARIOS.index(fin)+1]
                        ocupacion['horas'].update(horas)
                        if c[2] in MATERIAS:
                            ocupacion['profesores'].update(horas)
                            ocupacion['aulas'].update(horas)

                # Buscar todos los horarios posibles primero
                posibles = [
                    h for h in HORARIOS
                    if (h not in ocupacion['horas'] and
                        HORARIOS.index(h) + DURACION_CLASE <= len(HORARIOS) and
                        not any(
                            h_bloque in ocupacion['profesores'] or
                            h_bloque in ocupacion['aulas']
                            for h_bloque in HORARIOS[HORARIOS.index(h):HORARIOS.index(h)+DURACION_CLASE]
                        ))
                ]

                if posibles:
                    # Elegir el mejor horario (minimizando huecos)
                    inicio = random.choice(posibles)
                    fin = HORARIOS[HORARIOS.index(inicio) + DURACION_CLASE - 1]

                    # Añadir clase mutada
                    self.clases.append((nuevo_dia, f"{inicio} - {fin}", clase[2], clase[3], clase[4]))

                    # 3. Reajustar recesos automáticamente
                    self.reparar_horario()
                    self._fitness = None  # Invalidar fitness cache
                    return self

            # Si falla, revertir cambios y regenerar recesos
            self.clases.append(clase)
            self.reparar_horario()
            return self

########################################### EVALUACIÓN ########################################################

    @staticmethod
    def aula_es_valida(aula, materia):
        """Verifica si un aula es adecuada para una materia específica"""
        if materia in RESTRICCIONES_AULAS:
            return aula in RESTRICCIONES_AULAS[materia]
        return True  

     #=========================================================================================================#

    def calcular_fitness(self):
      if hasattr(self, '_fitness') and self._fitness is not None:
          return self._fitness

      # Inicializar penalizaciones para cada restricción
      P = [0.0] * 8  # P[0] a P[7] corresponden a P1 a P8

      # Estructuras para el análisis
      horas_materia = defaultdict(int)
      recesos_por_dia = defaultdict(int)
      horas_por_dia = defaultdict(float)
      ocupacion = {dia: {'horas': set(), 'profesores': set(), 'aulas': set()} for dia in DIAS}

      # 1. Verificar superposiciones (P7 - Restricción Dura)
      for clase in self.clases:
          dia = clase[0]
          inicio, fin = clase[1].split(" - ")
          horas = range(HORARIOS.index(inicio), HORARIOS.index(fin)+1)

          # Verificar superposición de horarios (P7)
          for h in horas:
              if h in ocupacion[dia]['horas']:
                  P[6] += 1  # P7: Superposición de clases
              ocupacion[dia]['horas'].add(h)

              if clase[2] != RECESO:
                  # Verificar asignación incorrecta de aulas (P8) 
                  if not Horario.aula_es_valida(clase[4], clase[2]):  
                      P[7] += 1  # Penalizar aula incorrecta

                  if h in ocupacion[dia]['profesores']:
                      P[6] += 0.5  # Mitad de penalización por profesor ocupado
                  if h in ocupacion[dia]['aulas']:
                      P[6] += 0.5  # Mitad de penalización por aula ocupada

                  ocupacion[dia]['profesores'].add(h)
                  ocupacion[dia]['aulas'].add(h)
                  horas_materia[clase[2]] += (len(horas) * 0.5)  # Horas totales
                  horas_por_dia[dia] += (len(horas) * 0.5)
              else:
                  recesos_por_dia[dia] += 1

      # 2. Verificar horas por materia (P6)
      for materia, horas in horas_materia.items():
          P[5] += min(1.0, abs(horas - 5.0) / 5.0)  # Normalizado [0-1]

      # 3. Verificar recesos (P2)
      for dia in DIAS:
          horas = horas_por_dia.get(dia, 0)
          recesos = recesos_por_dia.get(dia, 0)

          # Calcular recesos esperados
          if horas <= 3:
              esperados = 0
          elif horas <= 6:
              esperados = 1
          elif horas <= 9:
              esperados = 2
          else:
              esperados = 3

          P[1] += min(1.0, abs(recesos - esperados) / 3.0)  # Normalizado [0-1]

          # Verificar posición de recesos (parte de P2)
          clases_dia = [c for c in self.clases if c[0] == dia]
          if clases_dia:
              if clases_dia[0][2] == RECESO or clases_dia[-1][2] == RECESO:
                  P[1] += 0.3  # Penalización adicional

              # Verificar recesos consecutivos
              for i in range(len(clases_dia)-1):
                  if clases_dia[i][2] == RECESO and clases_dia[i+1][2] == RECESO:
                      P[1] += 0.5  # Penalización fuerte

      # 4. Verificar espacios entre clases (P3)
      for dia in DIAS:
          clases = sorted([c for c in self.clases if c[0] == dia and c[2] != RECESO],
                        key=lambda x: HORARIOS.index(x[1].split(" - ")[0]))

          for i in range(len(clases)-1):
              fin = HORARIOS.index(clases[i][1].split(" - ")[1])
              inicio = HORARIOS.index(clases[i+1][1].split(" - ")[0])
              if inicio > fin + 2:  # Más de 1 hora entre clases
                  P[2] += min(1.0, (inicio - fin - 2) / 4.0)  # Normalizado [0-1]

      # 5. Balance de carga (P4 y P5)
      promedio_horas = sum(horas_por_dia.values()) / len(DIAS)
      for dia, horas in horas_por_dia.items():
          # P4: Desbalance diario
          P[3] += min(1.0, abs(horas - promedio_horas) / 5.0)

          # P5: Carga excesiva
          if horas > 7.5:
              P[4] += min(1.0, (horas - 7.5) / 2.5)

      # 6. Duración de clases (P1)
      for clase in self.clases:
          if clase[2] in MATERIAS:
              duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
              if duracion != DURACION_CLASE:
                  P[0] += 0.5  # Penalización por sesión incorrecta

      # Calcular fitness final 
     
      penalizacion_blanda = sum(P[i] for i in range(6))  
      penalizacion_dura = sum(P[i] for i in range(6, 8)) * 2 

      self._fitness = 100 - (penalizacion_blanda + penalizacion_dura)
      return  self._fitness  

########################################### VISUALIZACIÓN ########################################################

    def __str__(self):
            output = []
            for dia in DIAS:
                output.append(f"\n{dia}:")
                clases_dia = [c for c in self.clases if c[0] == dia]
                for clase in sorted(clases_dia, key=lambda x: HORARIOS.index(x[1].split(" - ")[0])):
                    output.append(f"  {clase[1]:<12} {clase[2]:<12} {clase[3]:<10} {clase[4]}")
            return "\n".join(output)

########################################### FUNCIONES GENÉTICO ########################################################

def seleccion_torneo(poblacion, k):
    """Selección por torneo de tamaño k"""
    seleccionados = []
    for _ in range(len(poblacion)):
        participantes = random.sample(poblacion, k)
        ganador = max(participantes, key=lambda x: x.calcular_fitness())
        seleccionados.append(ganador)
    return seleccionados

       #=========================================================================================================#

def algoritmo_genetico():
    """Ejecuta el algoritmo genético para generar horarios"""
    # Generar población inicial
    poblacion = [Horario().generar_aleatorio() for _ in range(TAM_POBLACION)]

    mejor_fitness = -float('inf')
    generaciones_sin_mejora = 0
    mejor_horario = None

    for generacion in range(NUM_GENERACIONES):
        # Evaluar fitness
        for horario in poblacion:
            horario.calcular_fitness()

        # Selección
        seleccionados = seleccion_torneo(poblacion, TAM_TORNEO)


        #Cruce
        nueva_poblacion = []
        for i in range(0, len(seleccionados), 2):
            if i + 1 < len(seleccionados):
                padre1, padre2 = seleccionados[i], seleccionados[i+1]

                # Cruzar con probabilidad del 80%
                if random.random() < 0.8:
                    hijo1, hijo2 = padre1.cruzar_dias_avanzado(padre2)

                    # Reparar horarios si es necesario 
                    hijo1.reparar_horario()
                    hijo2.reparar_horario()

                    nueva_poblacion.extend([hijo1, hijo2])
                else:
                    nueva_poblacion.extend([padre1, padre2])

        # Mutación
        for i in range(len(nueva_poblacion)):
            if random.random() < PROB_MUTACION:
                nueva_poblacion[i].mutar()

        # Reemplazo generacional
        poblacion = nueva_poblacion

        # Encontrar el mejor de esta generación
        mejor_actual = max(poblacion, key=lambda x: x.calcular_fitness())
        fitness_actual = mejor_actual.calcular_fitness()

        # Verificar si hay mejora
        if fitness_actual > mejor_fitness:
            mejor_fitness = fitness_actual
            mejor_horario = mejor_actual
            generaciones_sin_mejora = 0
        else:
            generaciones_sin_mejora += 1

        # Criterio de paro temprano
        if generaciones_sin_mejora > 50 and generacion > 200:
            break

        # Mostrar progreso
        if generacion % 50 == 0:
            print(f"Generación {generacion}: Mejor fitness = {mejor_fitness}")

    return mejor_horario

########################################### RESUMEN ########################################################

def mostrar_resumen(horario):
    """Muestra un resumen del horario generado"""
    print("\n=== HORARIO OPTIMIZADO ===")
    print(horario)

    print("\n=== HORAS POR MATERIA ===")
    horas_materia = defaultdict(int)
    for clase in horario.clases:
        if clase[2] in MATERIAS:
            duracion = HORARIOS.index(clase[1].split(" - ")[1]) - HORARIOS.index(clase[1].split(" - ")[0]) + 1
            horas_materia[clase[2]] += duracion

    for materia, horas in horas_materia.items():
        print(f"{materia}: {horas} bloques de 30 min, en total({(horas/2)-1} horas)")

    print("\n=== RECESOS POR DÍA ===")
    recesos_por_dia = defaultdict(int)
    horas_clase_por_dia = defaultdict(float)
    for clase in horario.clases:
        if clase[2] == RECESO:
            recesos_por_dia[clase[0]] += 1
        elif clase[2] in MATERIAS:
            horas_clase_por_dia[clase[0]] += 2.5  

    for dia in DIAS:
        horas = horas_clase_por_dia.get(dia, 0)
        recesos = recesos_por_dia.get(dia, 0)
        print(f"{dia}: {horas} hrs de clase, {recesos} recesos")

    print("\n=== CARGA DIARIA (HORAS) ===")
    for dia in DIAS:
        horas = horas_clase_por_dia.get(dia, 0)
        print(f"{dia}: {horas} horas")

########################################### EJECUCIÓN ########################################################

if __name__ == "__main__":
    mejor_horario = algoritmo_genetico()
    mostrar_resumen(mejor_horario)
