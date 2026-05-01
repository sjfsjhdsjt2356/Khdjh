import discord
from discord.ext import commands, tasks
import asyncio

# --- [import time
import asyncio

class RefinedCore:
    def __init__(self):
        # Physical States
        self.temp = 20.0          # Celsius
        self.pressure = 0.0       # PSI
        self.water_level = 100.0  # Percentage
        self.rods_out = 0.0       # 0 = Fully Inserted, 100 = Fully Out
        
        # System Health
        self.pipe_integrity = 100.0
        self.is_scrammed = True
        
        # Power Generation
        self.mw_output = 0.0
        self.steam_flow = 0.0

    def process_tick(self):
        """The math that runs every few seconds"""
        if not self.is_scrammed:
            # 1. Rods generate heat (Exponentially if over 90%)
            heat_gain = (self.rods_out * 1.5)
            if self.rods_out > 90: heat_gain *= 1.2 
            self.temp += heat_gain
            
            # 2. Temperature creates Pressure (P = T * constant)
            self.pressure = self.temp * 2.5
            
            # 3. Steam Flow (Higher pressure = more steam for turbines)
            self.steam_flow = self.pressure * 0.1
            
            # 4. Water Level Consumption
            # If we are making steam, we are losing water
            self.water_level -= (self.steam_flow * 0.01)
            
        else:
            # Cooling down during SCRAM
            self.temp = max(20, self.temp - 5.0)
            self.pressure = max(0, self.pressure - 10.0)
            self.steam_flow = 0
            
        # Emergency Checks
        if self.temp > 1200 or self.pressure > 3000:
            return "MELTDOWN_IMMINENT"
        return "STABLE"

# Global Plant Object to hold all systems
class NuclearPlant:
    def __init__(self):
        self.core = RefinedCore()
        self.vault_money = 100000.0
        self.status = "OFFLINE"
        self.ticker_running = False

    async def start_global_tick(self):
        self.ticker_running = True
        while self.ticker_running:
            result = self.core.process_tick()
            if result == "MELTDOWN_IMMINENT":
                print("🚨 ALERT: Core Criticality Failure!")
            
            # We run the math every 5 seconds
            await asyncio.sleep(5)
          class PlantEconomy:
    def __init__(self):
        self.vault_balance = 50000.0  # Starting cash
        self.buy_price = 0.12         # Cost to buy 1MW from Gov (During Shutdown)
        self.sell_price = 0.08        # Profit from selling 1MW to City
        self.fixed_tax_rate = 500.0   # Gov Tax per tick (Land/Permits)
        self.budget_mode = "NORMAL"   # NORMAL, AUSTERITY, CRITICAL
        self.total_revenue_earned = 0.0

    def calculate_finances(self, current_mw, internal_usage):
        """Calculates profit or loss based on power flow"""
        net_power = current_mw - internal_usage
        
        if net_power > 0:
            # EXPORTING: Making money
            profit = net_power * self.sell_price
            self.vault_balance += profit
            self.total_revenue_earned += profit
            transaction_type = "REVENUE"
        else:
            # IMPORTING: Losing money (buying from Gov)
            cost = abs(net_power) * self.buy_price
            self.vault_balance -= cost
            transaction_type = "IMPORT_COST"

        # Apply Government Taxes
        self.vault_balance -= self.fixed_tax_rate
        
        # Bankruptcy Check
        if self.vault_balance <= 0:
            return "BANKRUPT"
        
        return transaction_type

# Updating the Global Plant Object
class NuclearPlant:
    def __init__(self):
        self.core = RefinedCore()
        self.economy = PlantEconomy()
        self.internal_need = 50.0  # MW needed just to keep lights/pumps on
        
    async def economy_tick(self):
        # This would be called inside the main loop
        status = self.economy.calculate_finances(
            self.core.mw_output, 
            self.internal_need
        )
        
        if status == "BANKRUPT":
            # Corporate pings would happen here
            print("🚨 FINANCIAL COLLAPSE: Vault is empty!")
          @bot.command()
async def vault(ctx):
    # Only Management or Corporate can see the exact numbers
    user_dept = get_user_dept(ctx.author.id) 
    if user_dept not in ["Management", "Corporate"]:
        return await ctx.send("❌ Confidential Financial Data. Clearance insufficient.")

    e = plant.economy
    embed = discord.Embed(title="🏦 PLANT VAULT & LEDGER", color=0x2ecc71)
    embed.add_field(name="Current Balance", value=f"${e.vault_balance:,.2f}", inline=False)
    embed.add_field(name="Export Rate", value=f"${e.sell_price}/MW", inline=True)
    embed.add_field(name="Import Rate", value=f"${e.buy_price}/MW", inline=True)
    embed.add_field(name="Budget Status", value=f"**{e.budget_mode}**", inline=True)
    
    await ctx.send(embed=embed)
import json
import os

class PlantDatabase:
    def __init__(self, file_path="plant_data.json"):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        """Loads data from file or creates a new structure if none exists."""
        if not os.path.exists(self.file_path):
            return {
                "users": {},      # user_id: {xp, balance, dept, rank, join_date}
                "global_stats": {
                    "total_mwh_generated": 0,
                    "meltdown_count": 0,
                    "plant_vault": 100000.0
                }
            }
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_data(self):
        """Saves current state to the JSON file."""
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_user(self, user_id):
        """Initializes a new user if they don't exist in the database."""
        u_id = str(user_id)
        if u_id not in self.data["users"]:
            self.data["users"][u_id] = {
                "xp": 0,
                "balance": 500,     # Personal wallet, not the vault
                "dept": "Unassigned",
                "rank": "Trainee",
                "last_shift": None
            }
        return self.data["users"][u_id]

    def update_user(self, user_id, key, value):
        u_id = str(user_id)
        if u_id in self.data["users"]:
            self.data["users"][u_id][key] = value
            self.save_data()

# Initialize Database
db = PlantDatabase()


# Initialize
plant = NuclearPlant()
def check_rank_up(user_id):
    user = db.get_user(user_id)
    dept = user["dept"]
    current_xp = user["xp"]
    
    # Referencing the RANKS dictionary from our earlier design
    available_ranks = RANKS.get(dept, [])
    new_rank = user["rank"]
    
    for r in available_ranks:
        if current_xp >= r["xp"]:
            new_rank = r["title"]
            
    if new_rank != user["rank"]:
        db.update_user(user_id, "rank", new_rank)
        return True, new_rank
    return False, user["rank"]
  @bot.command()
async def profile(ctx):
    user_data = db.get_user(ctx.author.id)
    
    embed = discord.Embed(title=f" Personnel File: {ctx.author.name}", color=0x3498db)
    embed.add_field(name="Department", value=f"🏢 {user_data['dept']}", inline=True)
    embed.add_field(name="Rank", value=f" {user_data['rank']}", inline=True)
    embed.add_field(name="Experience", value=f" {user_data['xp']} XP", inline=True)
    embed.add_field(name="Personal Wallet", value=f"💵 ${user_data['balance']}", inline=True)
    
    # Logic to show a progress bar to next rank
    await ctx.send(embed=embed)

class HRSystem:
    def __init__(self, database):
        self.db = database
        self.pending_apps = {} # user_id: requested_dept

    async def apply(self, ctx, dept_name):
        user_id = ctx.author.id
        if dept_name not in RANKS:
            return await ctx.send(f"❌ `{dept_name}` is not a valid department!")
        
        self.pending_apps[user_id] = dept_name
        await ctx.send(f"📝 **APPLICATION FILED**: {ctx.author.mention} has applied for **{dept_name}**. Awaiting SM/PD approval.")

    async def hire(self, ctx, member: discord.Member):
        # 1. Permission Check
        manager_roles = ["Shift Manager", "Plant Director"]
        if not any(r.name in manager_roles for r in ctx.author.roles):
            return await ctx.send("❌ You don't have hiring authority!")

        # 2. Process Application
        if member.id not in self.pending_apps:
            return await ctx.send("❌ This user has no pending application.")

        dept = self.pending_apps.pop(member.id)
        
        # 3. Update Database
        self.db.update_user(member.id, "dept", dept)
        self.db.update_user(member.id, "rank", "Intern") # Start at the bottom
        
        await ctx.send(f"✅ **WELCOME ABOARD**: {member.mention} has been hired into **{dept}** by {ctx.author.name}!")

    async def fire_personnel(self, ctx, member: discord.Member):
        # PD can fire anyone. SM cannot fire Chiefs.
        is_pd = "Plant Director" in [r.name for r in ctx.author.roles]
        is_sm = "Shift Manager" in [r.name for r in ctx.author.roles]
        
        target_data = self.db.get_user(member.id)
        
        if "Corporate" in target_data['dept']:
            return await ctx.send(" You can't fire the investors.")

        if is_pd or (is_sm and "Chief" not in target_data['rank']):
            self.db.update_user(member.id, "dept", "Unassigned")
            self.db.update_user(member.id, "rank", "Trainee")
            await ctx.send(f" **TERMINATED**: {member.mention} has been removed from their position.")
        else:
            await ctx.send("❌ Authority Error: You cannot fire a Department Chief.")

# Initialize
hr = HRSystem(db)
class ReactorHall:
    def __init__(self, plant_object):
        self.plant = plant_object

    async def adjust_rods(self, ctx, amount: int):
        """amount can be positive (pulling out) or negative (pushing in)"""
        user_data = db.get_user(ctx.author.id)
        
        # 1. Rank Check (Operations Senior RO+ only)
        if user_data['dept'] != "Operations" or user_data['xp'] < 1000:
            return await ctx.send("❌ You don't have the 'Senior RO' clearance to move control rods!")

        # 2. Update Rod Position
        core = self.plant.core
        new_pos = core.rods_out + amount
        core.rods_out = max(0, min(100, new_pos)) # Keep between 0 and 100
        
        # 3. Automatic Startup
        if core.rods_out > 5 and core.is_scrammed:
            core.is_scrammed = False
            self.plant.status = "ONLINE"
            await ctx.send("☢️ **CRITICALITY REACHED**: Reactor is now self-sustaining.")

        await ctx.send(f"🕹️ **ROD ADJUSTMENT**: Rods are now at **{core.rods_out}%** OUT. (Temp: {core.temp:.1f}°C)")

    async def manual_scram(self, ctx):
        """Emergency Shutdown"""
        core = self.plant.core
        core.rods_out = 0
        core.is_scrammed = True
        self.plant.status = "SCRAMMED"
        
        await ctx.send("🚨 **REACTOR SCRAMMED**: All control rods inserted. Cooling cycle initiated.")

# Connecting to the main Bot Commands
@bot.command()
async def rods(ctx, amount: int):
    await reactor_hall.adjust_rods(ctx, amount)

@bot.command()
async def scram(ctx):
    await reactor_hall.manual_scram(ctx)
  async def water_monitor(self):
    core = self.plant.core
    if core.water_level < 30:
        # Trigger an alert in the PA system
        await pa_system.broadcast("⚠️ **LOW WATER LEVEL**: Reactor core exposure risk! Increase feedwater flow!")
    
    if core.water_level <= 0:
        # Meltdown Logic
        self.plant.status = "MELTDOWN"
        await pa_system.broadcast("☢️ **CORE MELTDOWN**: The fuel has melted through the containment floor. Plant lost.")
 class TurbineSystem:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.rpm = 0.0
        self.throttle = 0.0     # 0 to 100% steam admission
        self.target_rpm = 3600  # Standard for 60Hz grid sync
        self.is_synced = False
        self.health = 100.0

    def calculate_mechanics(self):
        core = self.plant.core
        
        # 1. Steam Pressure provides torque
        # No steam = Turbine starts slowing down due to friction
        if core.steam_flow > 0 and self.throttle > 0:
            torque = (core.steam_flow * (self.throttle / 100))
            self.rpm += (torque * 0.5)
        else:
            self.rpm = max(0, self.rpm - 2.5) # Friction loss

        # 2. Centrifugal Stress (Overspeed Risk)
        if self.rpm > 4000:
            damage = (self.rpm - 4000) * 0.01
            self.health -= damage
            
        # 3. Power Conversion
        # If synced, RPM determines MW output
        if self.is_synced:
            # If RPM drops below 3550 or above 3650 while synced, the breaker trips!
            if not (3550 <= self.rpm <= 3650):
                self.is_synced = False
                self.plant.core.mw_output = 0
                return "GRID_TRIP"
            
            self.plant.core.mw_output = (self.rpm / 3600) * (core.steam_flow * 2)
        
        return "STABLE"

# RO Command to control steam admission
@bot.command()
async def throttle(ctx, setting: int):
    user_data = db.get_user(ctx.author.id)
    if user_data['dept'] != "Operations":
        return await ctx.send("❌ Only Operations can access the Turbine Throttle.")

    plant.turbine.throttle = max(0, min(100, setting))
    await ctx.send(f" **TURBINE THROTTLE**: Set to **{setting}%**. RPM: {plant.turbine.rpm:.1f}")
  @bot.command()
async def sync(ctx):
    t = plant.turbine
    # Check if RPM is in the 'Green Zone' (3590 - 3610)
    if 3590 <= t.rpm <= 3610:
        t.is_synced = True
        await ctx.send("⚡ **GRID SYNC SUCCESSFUL**: Turbine is locked to 60Hz. Power is flowing to the city!")
        db.update_user(ctx.author.id, "xp", db.get_user(ctx.author.id)['xp'] + 50)
    else:
        # If they sync at the wrong speed, they damage the generator
        t.health -= 15
        await ctx.send(f"💥 **SYNC FAILED**: Frequency mismatch! Turbine vibrated violently at {t.rpm:.1f} RPM. Equipment damaged!")
     class CoolingSystem:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.condenser_temp = 35.0  # Celsius (Ideal is 30-40)
        self.vacuum_pressure = 1.0  # Bar (1.0 is perfect vacuum, 0.0 is failed)
        self.tower_fans_on = False
        self.water_pump_active = False

    def calculate_cooling(self):
        t = self.plant.turbine
        
        # 1. Steam creates heat in the condenser
        # The more steam the turbine exhausts, the hotter the condenser gets
        if t.throttle > 0:
            self.condenser_temp += (t.throttle * 0.05)
        
        # 2. Fans and Pumps remove heat
        cooling_power = 0
        if self.tower_fans_on: cooling_power += 1.2
        if self.water_pump_active: cooling_power += 2.5
        
        self.condenser_temp = max(25, self.condenser_temp - cooling_power)

        # 3. Efficiency/Vacuum Calculation
        # Physics: Hot condenser = Bad vacuum = Turbine drag
        if self.condenser_temp > 50:
            self.vacuum_pressure = max(0, self.vacuum_pressure - 0.02)
        else:
            self.vacuum_pressure = min(1.0, self.vacuum_pressure + 0.01)

        # 4. Impact on Turbine
        # If vacuum is lost (0.0), the turbine literally cannot spin
        if self.vacuum_pressure < 0.3:
            t.rpm -= 10.0 # Heavy drag
            return "LOW_VACUUM_WARNING"
        
        return "STABLE"

# Operations Command for Cooling
@bot.command()
async def cooling(ctx, component: str, action: str):
    """Example: !cooling fans on"""
    user_data = db.get_user(ctx.author.id)
    if user_data['dept'] != "Operations":
        return await ctx.send("❌ Access Denied.")

    if component == "fans":
        plant.cooling.tower_fans_on = (action.lower() == "on")
    elif component == "pumps":
        plant.cooling.water_pump_active = (action.lower() == "on")
    
    await ctx.send(f"❄️ **COOLING UPDATE**: {component} {action.upper()}. Condenser: {plant.cooling.condenser_temp:.1f}°C")
class FeedwaterSystem:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.pump_1_power = 0.0  # 0 to 100%
        self.pump_2_power = 0.0
        self.valve_opening = 0.0 # Flow control valve
        self.total_inflow = 0.0

    def calculate_flow(self):
        core = self.plant.core
        
        # 1. Total Pump Pressure
        # Each pump contributes pressure. If they are off, pressure is 0.
        pump_pressure = (self.pump_1_power + self.pump_2_power) * 25.0
        
        # 2. The Pressure Battle
        # Flow only happens if Pump Pressure > Reactor Pressure
        pressure_diff = pump_pressure - core.pressure
        
        if pressure_diff > 0:
            # Flow is limited by the valve opening
            self.total_inflow = (pressure_diff * 0.01) * (self.valve_opening / 100)
        else:
            self.total_inflow = 0.0
            if core.pressure > 500 and pump_pressure < core.pressure:
                return "BACKFLOW_WARNING" # Steam pushing back into pipes!

        # 3. Update Reactor Water Level
        core.water_level = min(100, core.water_level + self.total_inflow)
        
        return "STABLE"

# Maintenance or Ops Command to control pumps
@bot.command()
async def pump(ctx, num: int, power: int):
    user_data = db.get_user(ctx.author.id)
    if user_data['dept'] not in ["Operations", "Maintenance"]:
        return await ctx.send("❌ Access Denied: Requires Engineering Clearance.")

    if num == 1: plant.feedwater.pump_1_power = max(0, min(100, power))
    elif num == 2: plant.feedwater.pump_2_power = max(0, min(100, power))
    
    await ctx.send(f"⚙️ **PUMP {num}**: Adjusted to **{power}%**. Inflow: {plant.feedwater.total_inflow:.2f} L/s")

@bot.command()
async def valve(ctx, setting: int):
    plant.feedwater.valve_opening = max(0, min(100, setting))
    await ctx.send(f"🚿 **FEEDWATER VALVE**: Set to **{setting}%**.")
class ElectricalSystem:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.main_bus_active = False    # Connected to Turbine
        self.aux_bus_active = True      # Connected to Gov/External Grid
        self.emergency_bus_active = False # Connected to Diesel Generators
        self.grid_load = 0.0

    def get_power_source(self):
        """Determines if the plant has 'House Power' to run pumps/lights"""
        # Priority 1: Main Generator (Self-Sustaining)
        if self.main_bus_active and self.plant.turbine.is_synced:
            return "MAIN_GENERATOR"
        # Priority 2: External Grid (Costs money)
        if self.aux_bus_active:
            return "EXTERNAL_GRID"
        # Priority 3: Emergency Diesels (Limited Fuel)
        if self.emergency_bus_active:
            return "EMERGENCY_DIESEL"
        
        return "BLACKOUT"

    def calculate_bus_stability(self):
        source = self.get_power_source()
        
        if source == "BLACKOUT":
            # If there's no power, all automated systems fail
            self.plant.feedwater.pump_1_power = 0
            self.plant.feedwater.pump_2_power = 0
            self.plant.cooling.tower_fans_on = False
            return "CRITICAL_BLACKOUT"
            
        return "STABLE"

# Management Command to switch power sources
@bot.command()
async def switch(ctx, bus: str, state: str):
    """Usage: !switch main on | !switch aux off"""
    user_data = db.get_user(ctx.author.id)
    if user_data['dept'] not in ["Operations", "Maintenance"]:
        return await ctx.send("❌ Electrical switching requires engineering clearance.")

    active = (state.lower() == "on")
    
    if bus == "main": plant.electrical.main_bus_active = active
    elif bus == "aux": plant.electrical.aux_bus_active = active
    elif bus == "emergency": plant.electrical.emergency_bus_active = active
    
    await ctx.send(f"🔌 **ELECTRICAL BUS**: {bus.upper()} is now {'CONNECTED' if active else 'DISCONNECTED'}.")
class EmergencyDiesel:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.is_running = False
        self.warmup_progress = 0  # 0 to 100
        self.fuel_level = 100.0   # Percentage
        self.load_capacity = 25.0 # MW (Enough for pumps, not for profit)

    def process_diesel_tick(self):
        if self.is_running:
            # 1. Warmup Logic (Takes time to reach full speed)
            if self.warmup_progress < 100:
                self.warmup_progress += 20  # Takes 5 ticks to warm up
                return "WARMING_UP"

            # 2. Fuel Consumption
            # Diesels eat fuel fast!
            self.fuel_level -= 0.5 
            if self.fuel_level <= 0:
                self.fuel_level = 0
                self.is_running = False
                self.warmup_progress = 0
                return "OUT_OF_FUEL"

            # 3. Power Supply
            # Connects to the Emergency Bus from Segment 10
            self.plant.electrical.emergency_bus_active = True
            return "POWERING_SYSTEMS"
        
        return "OFFLINE"

# Command to start the engines
@bot.command()
async def edg(ctx, action: str):
    """Usage: !edg start | !edg stop"""
    user_data = db.get_user(ctx.author.id)
    if user_data['dept'] not in ["Operations", "Maintenance", "Security"]:
        return await ctx.send("❌ Access Denied.")

    if action.lower() == "start":
        if plant.edg.fuel_level <= 0:
            return await ctx.send("⚠️ **EDG FAILURE**: Fuel tanks are empty! Call Logistics!")
        
        plant.edg.is_running = True
        await ctx.send("🚜 **EDG STARTING**: Engines cranking... Warmup sequence initiated (30s).")
    
    elif action.lower() == "stop":
        plant.edg.is_running = False
        plant.edg.warmup_progress = 0
        plant.electrical.emergency_bus_active = False
        await ctx.send("🛑 **EDG SHUTDOWN**: Emergency engines stopped.")
      
import random

class MaintenanceDept:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.parts_inventory = {"Gaskets": 5, "Bearings": 2, "Electronics": 3}
        self.tool_kit = ["Wrench", "Soldering Iron", "Welder", "Multimeter"]

    def get_status_report(self):
        """Diagnostic tool to see hidden health stats"""
        report = {
            "Turbine Bearings": self.plant.turbine.health,
            "Feedwater Pump 1": 100.0, # Placeholder for pump health
            "Pipe Integrity": self.plant.piping.integrity,
            "EDG Engine": self.plant.edg.fuel_level # Placeholder for EDG health
        }
        return report

# --- Commands ---

@bot.command()
async def diagnose(ctx, component: str):
    user_data = db.get_user(ctx.author.id)
    if user_data['dept'] != "Maintenance":
        return await ctx.send("❌ You don't have the technical training to run diagnostics.")

    # Simulated "Vibration" or "Heat" signatures
    faults = ["Grinding Noise", "Overheating", "Fluid Leak", "Electrical Arc"]
    current_fault = random.choice(faults)
    
    await ctx.send(f"🔍 **DIAGNOSTIC RESULT**: Component `{component}` is showing signs of: **{current_fault}**.")
    await ctx.send("💡 *Hint: Use !repair [component] [tool] [part]*")

@bot.command()
async def repair(ctx, component: str, tool: str, part: str):
    user_data = db.get_user(ctx.author.id)
    if user_data['dept'] != "Maintenance":
        return await ctx.send("❌ Access Denied.")

    # 1. Inventory Check
    if self.parts_inventory.get(part, 0) <= 0:
        return await ctx.send(f"❌ We are out of **{part}**! Logistics (LO) needs to deliver more.")

    # 2. Logic for Repair Success
    success = False
    if component == "pipes" and tool == "Welder" and part == "Gaskets":
        self.plant.piping.integrity = min(100, self.plant.piping.integrity + 25)
        success = True
    elif component == "turbine" and tool == "Wrench" and part == "Bearings":
        self.plant.turbine.health = min(100, self.plant.turbine.health + 20)
        success = True

    if success:
        self.parts_inventory[part] -= 1
        db.update_user(ctx.author.id, "xp", user_data['xp'] + 40)
        await ctx.send(f"🛠️ **SUCCESS**: {ctx.author.name} repaired the {component}! (+40 XP)")
    else:
        await ctx.send(f"⚠️ **FAIL**: That tool/part combination didn't work. The {component} is still failing!")
      class LogisticsDept:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.fleet = {
            "Small Van": {"status": "IDLE", "capacity": 5, "fuel": 100, "cost": 500},
            "Cargo Truck": {"status": "IDLE", "capacity": 20, "fuel": 100, "cost": 2000},
            "Nuclear Semi": {"status": "IDLE", "capacity": 50, "fuel": 100, "cost": 15000}
        }
        self.warehouse = {"Uranium": 10, "Diesel": 100, "Parts": 5}

    async def dispatch(self, ctx, vehicle_type: str, resource: str):
        user_data = db.get_user(ctx.author.id)
        if user_data['dept'] != "Logistics":
            return await ctx.send("❌ You don't have a Commercial Driver's License (CDL)!")

        # 1. Vehicle Check
        if vehicle_type not in self.fleet:
            return await ctx.send("❌ That vehicle isn't in our fleet.")
        
        veh = self.fleet[vehicle_type]
        if veh["status"] != "IDLE":
            return await ctx.send(f"❌ The {vehicle_type} is already out on a delivery!")

        # 2. Budget Check (Does the Plant Vault have money for the trip?)
        if self.plant.economy.vault_balance < veh["cost"]:
            return await ctx.send("❌ **BUDGET REJECTED**: The Plant Director hasn't authorized funds for this trip!")

        # 3. Start Trip
        self.plant.economy.vault_balance -= veh["cost"]
        veh["status"] = "EN_ROUTE"
        
        await ctx.send(f" **DISPATCHED**: {ctx.author.name} is driving the {vehicle_type} to pick up **{resource}**.")
        
        # Simulate travel time (30 seconds to 2 minutes)
        await asyncio.sleep(60) 
        
        # 4. Return & Stocking
        veh["status"] = "IDLE"
        amount = 10 if resource == "Uranium" else 50
        self.warehouse[resource] += amount
        
        # If it was parts, we push them to Maintenance
        if resource == "Parts":
            self.plant.maintenance.parts_inventory["Gaskets"] += 5
            
        await ctx.send(f"📦 **DELIVERY COMPLETE**: {vehicle_type} returned. **+{amount} {resource}** added to stores.")
        db.update_user(ctx.author.id, "xp", user_data['xp'] + 100)
import random

class SecurityDept:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.safety_score = 100.0   # 0 to 100
        self.alert_level = "GREEN"  # GREEN, YELLOW, ORANGE, RED
        self.is_patrolling = False
        self.armory = {"Body Armor": 10, "Non-Lethal": 50, "Authorized Firearms": 5}

    def update_safety(self):
        """Passive decay of safety if no one patrols"""
        if not self.is_patrolling:
            self.safety_score -= 0.1
        
        # Determine Alert Level
        if self.safety_score > 80: self.alert_level = "GREEN"
        elif self.safety_score > 50: self.alert_level = "YELLOW"
        else: self.alert_level = "RED"

    async def patrol(self, ctx):
        user_data = db.get_user(ctx.author.id)
        if user_data['dept'] != "Security":
            return await ctx.send("❌ You are not authorized to conduct security patrols.")

        self.is_patrolling = True
        await ctx.send(f"  **PATROL STARTED**: {ctx.author.name} is checking the perimeter...")
        
        # Patrol takes time
        await asyncio.sleep(45)
        
        self.safety_score = min(100, self.safety_score + 15)
        self.is_patrolling = False
        await ctx.send(f"✅ **PATROL COMPLETE**: Perimeter secure. Safety Score: **{self.safety_score:.1f}%**")
        db.update_user(ctx.author.id, "xp", user_data['xp'] + 50)

    async def escort_truck(self, ctx):
        """Reduces the chance of a Logistics hijack"""
        user_data = db.get_user(ctx.author.id)
        if user_data['dept'] != "Security":
            return await ctx.send("❌ Only Security can provide armed escorts.")

        # Logic to link with a currently 'EN_ROUTE' Logistics vehicle
        active_trucks = [v for k, v in self.plant.logistics.fleet.items() if v["status"] == "EN_ROUTE"]
        
        if not active_trucks:
            return await ctx.send("❌ No Logistics vehicles currently need an escort.")
        
        await ctx.send("🛡️ **ESCORT ACTIVE**: Security is trailing the shipment. Hijack risk reduced to 0%.")
      @bot.command()
async def detain(ctx):
    # Only works if there is an active 'Intruder Alert'
    if plant.security.alert_level != "RED":
        return await ctx.send("❌ No active intruder threats detected.")
    
    success_chance = 70 if "Chief" in db.get_user(ctx.author.id)['rank'] else 40
    
    if random.randint(1, 100) <= success_chance:
        await ctx.send(f" **APPREHENDED**: {ctx.author.mention} has detained the intruder! Plant assets secured.")
        plant.security.safety_score += 10
    else:
        await ctx.send(" **ESCAPE**: The intruder slipped away! Check the warehouse for missing parts.")
        plant.logistics.warehouse["Parts"] -= 1
      class SCADAInterface(discord.ui.View):
    def __init__(self, plant_object):
        super().__init__(timeout=None) # Keeps the buttons active forever
        self.plant = plant_object

    def create_embed(self):
        """Generates the live status report"""
        c = self.plant.core
        t = self.plant.turbine
        e = self.plant.economy
        
        status_emoji = "🟢" if self.plant.status == "ONLINE" else "🔴"
        
        embed = discord.Embed(title=f"{status_emoji} CENTRAL CONTROL SYSTEM", color=0x2f3136)
        
        # Column 1: Reactor
        reactor_stats = (
            f"**Temp:** {c.temp:.1f}°C\n"
            f"**Pressure:** {c.pressure:.0f} PSI\n"
            f"**Water:** {c.water_level:.1f}%"
        )
        embed.add_field(name="  REACTOR CORE", value=reactor_stats, inline=True)
        
        # Column 2: Turbine/Grid
        turbine_stats = (
            f"**RPM:** {t.rpm:.0f}\n"
            f"**Output:** {c.mw_output:.1f} MW\n"
            f"**Sync:** {'✅' if t.is_synced else '❌'}"
        )
        embed.add_field(name="🌀 TURBINE ROOM", value=turbine_stats, inline=True)
        
        # Column 3: Finance
        vault_stats = (
            f"**Balance:** ${e.vault_balance:,.2f}\n"
            f"**Budget:** {e.budget_mode}"
        )
        embed.add_field(name="💰 PLANT VAULT", value=vault_stats, inline=True)

        embed.set_footer(text="V2 Refined • Use buttons below to interact")
        return embed

    # --- Buttons for the RO ---

    @discord.ui.button(label="SCRAM", style=discord.ButtonStyle.danger, custom_id="scram_btn")
    async def scram_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check permissions via the DB
        user_data = db.get_user(interaction.user.id)
        if user_data['dept'] != "Operations":
            return await interaction.response.send_message("❌ Unauthorized access to Emergency Shutoff.", ephemeral=True)
            
        self.plant.core.is_scrammed = True
        self.plant.core.rods_out = 0
        await interaction.response.send_message(f"🚨 **SCRAM INITIATED** by {interaction.user.display_name}!", ephemeral=False)

    @discord.ui.button(label="Rods +10%", style=discord.ButtonStyle.primary)
    async def rod_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.plant.core.rods_out = min(100, self.plant.core.rods_out + 10)
        await interaction.response.edit_message(embed=self.create_embed()) # Instant update
      async def update_scada_message(message_obj):
    while True:
        new_view = SCADAInterface(plant)
        await message_obj.edit(embed=new_view.create_embed(), view=new_view)
        await asyncio.sleep(10) # Refresh rate
      class ManagementSuite:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.corporate_dividend_rate = 0.15 # 15% of all profits go to investors
        self.bonus_pool = 0.0
        self.budget_allocation = {
            "Maintenance": 1.0, # Multipliers for part costs
            "Security": 1.0,
            "Logistics": 1.0
        }

    def process_corporate_cut(self, profit):
        """Investors take their share before the vault sees it"""
        dividend = profit * self.corporate_dividend_rate
        actual_profit = profit - dividend
        return actual_profit, dividend

    async def set_policy(self, ctx, department: str, policy: str):
        """PD can set policies: AUSTERITY, NORMAL, or AGGRESSIVE"""
        user_data = db.get_user(ctx.author.id)
        if user_data['rank'] != "Plant Director":
            return await ctx.send("❌ Only the Plant Director can set fiscal policy.")

        if policy == "AUSTERITY":
            self.budget_allocation[department] = 0.5 # Half budget, causes 'Strike' risk
        elif policy == "AGGRESSIVE":
            self.budget_allocation[department] = 1.5 # High budget, boost performance
            
        await ctx.send(f"📉 **FISCAL POLICY**: {department} is now on **{policy}** mode.")
      async def check_corporate_standing(self):
    vault = self.plant.economy.vault_balance
    if vault < 1000:
        # Corporate sends a warning
        await pa_system.broadcast("📧 **INCOMING CORPORATE MEMO**: PD, your performance is unsatisfactory. Funding is critical. Fix it or be replaced.")
    
    if vault <= 0:
        # The ultimate fail state
        await pa_system.broadcast(" **CORPORATE TAKEOVER**: The Plant is bankrupt. The Plant Director has been fired.")
        # Logic to reset the PD role to Unassigned
import random

class ChaosEngine:
    def __init__(self, plant_object):
        self.plant = plant_object
        self.active_disaster = None

    async def roll_for_chaos(self):
        # 5% chance of a disaster every "Tick"
        if random.randint(1, 100) <= 5:
            await self.trigger_disaster()

    async def trigger_disaster(self):
        events = [
            "GRID_SURGE",      # Blows the electrical buses
            "PIPE_BURST",      # Massive water loss
            "SEISMIC_EVENT",   # Damages everything 10%
            "CYBER_ATTACK",    # SCADA buttons stop working
            "FUEL_LEAK"        # EDG fuel drains to zero
        ]
        
        self.active_disaster = random.choice(events)
        await self.announce_disaster()

    async def announce_disaster(self):
        msg = ""
        if self.active_disaster == "GRID_SURGE":
            msg = "⚡ **ELECTRICAL CRITICAL**: A massive surge hit the grid! All Buses have TRIPPED!"
            self.plant.electrical.main_bus_active = False
            self.plant.electrical.aux_bus_active = False
            
        elif self.active_disaster == "SEISMIC_EVENT":
            msg = " **EARTHQUAKE**: The facility is shaking! Integrity and Turbine health dropping!"
            self.plant.piping.integrity -= 20
            self.plant.turbine.health -= 15
            
        elif self.active_disaster == "CYBER_ATTACK":
            msg = "**MALWARE DETECTED**: Control systems are unresponsive! (Buttons locked for 60s)"
            # Logic to disable SCADA view interaction temporarily
            
        # Send to a general 'Alarms' channel
        channel = bot.get_channel(ALARM_CHANNEL_ID)
        await channel.send(f"🚨 **MAJOR DISASTER**: {msg} 🚨🚨")
      
] ---
# (RefinedCore, PlantDatabase, HRSystem, ReactorHall, etc.)

class NuclearPlant:
    def __init__(self):
        # The Core State
        self.db = PlantDatabase()
        self.core = RefinedCore()
        self.economy = PlantEconomy(self)
        self.turbine = TurbineSystem(self)
        self.cooling = CoolingSystem(self)
        self.feedwater = FeedwaterSystem(self)
        self.piping = PipingSystem(self)
        self.electrical = ElectricalSystem(self)
        self.edg = EmergencyDiesel(self)
        self.logistics = LogisticsDept(self)
        self.security = SecurityDept(self)
        self.status = "OFFLINE"

# --- INITIALIZATION ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
plant = NuclearPlant()

# --- THE HEARTBEAT (The Master Loop) ---
@tasks.loop(seconds=5)
async def plant_heartbeat():
    """This runs every 5 seconds to update the entire simulation."""
    # 1. Physics & Thermodynamics
    plant.core.calculate_physics()
    plant.turbine.calculate_mechanics()
    plant.cooling.calculate_cooling()
    plant.feedwater.calculate_flow()
    plant.piping.calculate_integrity()
    
    # 2. Economy & Electrical
    plant.economy.process_tick()
    plant.electrical.calculate_bus_stability()
    plant.edg.process_diesel_tick()
    
    # 3. Security & Chaos
    plant.security.update_safety()
    # roll_for_chaos() logic here...

    # 4. Check for Meltdown
    if plant.core.temp > 3000:
        plant.status = "MELTDOWN"
        # Trigger global alarm

# --- THE STARTUP COMMAND ---
@bot.event
async def on_ready():
    print(f"✅ Simulation Online: {bot.user}")
    # Start the heartbeat loop
    if not plant_heartbeat.is_running():
        plant_heartbeat.start()

# --- THE FINAL LINE (CRITICAL) ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)

