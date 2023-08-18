from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

class Semaforo(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.estado = "verde"
        self.ticks = 0
    
    def step(self):
        self.ticks += 1
        if self.ticks == 6:
            self.estado = "rojo"
        elif self.ticks == 9:
            self.estado = "verde"
            self.ticks = 0

class Peaton(Agent):
    def __init__(self, unique_id, model, lado):
        super().__init__(unique_id, model)
        self.lado = lado
    
    def step(self):
        cell = self.model.grid.get_cell_list_contents([self.pos])
        if cell:
            cell = cell[0]
            if isinstance(cell, Semaforo) and cell.estado == "verde" and cell.ticks < 3:
                self.model.grid.move_agent(self, (self.pos[0], 1 - self.pos[1]))

class Guardia(Agent):
    def step(self):
        cell = self.model.grid.get_cell_list_contents([self.pos])
        if cell:
            cell = cell[0]
            if isinstance(cell, Semaforo) and cell.ticks >= 9:
                neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
                for neighbor in neighbors:
                    if isinstance(neighbor, Peaton):
                        self.model.grid.move_agent(neighbor, (neighbor.pos[0], 1 - neighbor.pos[1]))
                cell.ticks = 0

class Vehiculo(Agent):
    def step(self):
        cell = self.model.grid.get_cell_list_contents([self.pos])
        if cell:
            cell = cell[0]
            if isinstance(cell, Guardia):
                neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
                for neighbor in neighbors:
                    if isinstance(neighbor, Peaton):
                        self.model.grid.move_agent(neighbor, (neighbor.pos[0], 1 - neighbor.pos[1]))

class CruceModel(Model):
    def __init__(self, width, height, num_peatones):
        self.num_peatones = num_peatones
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        
        # Crear agentes
        semaforo = Semaforo(0, self)
        self.schedule.add(semaforo)
        self.grid.place_agent(semaforo, (1, 1))
        
        guardia = Guardia(1, self)
        self.schedule.add(guardia)
        self.grid.place_agent(guardia, (0, 0))
        
        for i in range(self.num_peatones):
            lado = "tec" if random.random() < 0.5 else "e1"
            peaton = Peaton(i + 2, self, lado)
            self.schedule.add(peaton)
            if lado == "tec":
                self.grid.place_agent(peaton, (0, 1))
            else:
                self.grid.place_agent(peaton, (1, 0))
        
        for i in range(2):
            vehiculo = Vehiculo(i + self.num_peatones + 2, self)
            self.schedule.add(vehiculo)
            if i == 0:
                self.grid.place_agent(vehiculo, (0, 1))
            else:
                self.grid.place_agent(vehiculo, (1, 0))
        
        self.datacollector = DataCollector(
            agent_reporters={"Estado Semaforo": "estado"}
        )
        
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# Parámetros del modelo
width = 2
height = 2
num_peatones = 6

# Crear el modelo
model = CruceModel(width, height, num_peatones)

# Simular
for i in range(20):
    print(f"Tick {i}")
    model.step()

# Mostrar los datos recopilados del semáforo
print(model.datacollector.get_agent_vars_dataframe().head())
