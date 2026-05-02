import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import time
import asyncio
import random
import os

# ==========================================
# [1] XP & RANKING ARCHITECTURE (The V3 Math)
# ==========================================
def calculate_rank_from_xp(xp, dept):
    """
    Standard: 1,000 baseline, 3x scaling.
    Management: 1,000 baseline, 5x scaling.
    Specific Milestones: Shift Manager (20K), PD (60K).
    Heads: Rank Below * 4.
    """
    if dept == "Management":
        if xp >= 60000: return "Plant Director"
        if xp >= 20000: return "Shift Manager"
        if xp >= 5000:  return "Senior Manager"
        if xp >= 1000:  return "Shift Supervisor"
        return "Management Trainee"
    
    if dept == "Unemployed":
        return "None"

    # --- Standard Departments (Operations, Maintenance, Security, Logistics, Corporate) ---
    # Requirement: 1k -> 3k -> 9k -> 27k
    # Head Requirement: 27k * 4 = 108k
    if xp >= 108000: return f"Head of {dept}"
    if xp >= 27000:  return "Specialist"
    if xp >= 9000:   return "Senior Staff"
    if xp >= 3000:   return "Standard Staff"
    if xp >= 1000:   return "Junior Staff"
    return f"{dept} Trainee"

# ==========================================
# [2] PERSISTENT DATABASE (No-Wipe Memory)
# ==========================================
class PlantDatabase:
    def __init__(self):
        self.file = "facility_v3_data.json"
        self.data = self.load()

    def load(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                return json.load(f)
        return {
            "users": {}, 
            "global_stats": {
                "facility_funds": 1000000,
                "power_grid_mode": "External",
                "external_grid_damaged": False,
                "melt_count": 0
            }
        }

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_user(self, uid):
        uid = str(uid)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "xp": 0, 
                "dept": "Unemployed", 
                "rank": "None", 
                "balance": 500, 
                "cooldown": 0,
                "pending_dept": None
            }
        return self.data["users"][uid]

# ==========================================
# [3] THE MASTER CONNECTOR (Plant Class)
# ==========================================
class NuclearPlant:
    def __init__(self):
        self.db = PlantDatabase()
        
        # System placeholders (To be defined in Segment 2)
        self.core = None
        self.cooling = None
        self.grid = None
        self.turbines = None
        self.logistics = None
        
        self.status = "STABLE"
        self.meltdown_active = False

    def tick(self):
        """The Heartbeat Logic"""
        if self.meltdown_active:
            return "BOOM"
        
        # Physics chain
        self.grid.calculate()
        self.cooling.calculate()
        self.core.calculate()
        self.turbines.calculate()

        if self.core.integrity <= 0:
            self.meltdown_active = True
            return "BOOM"
        return "OK"

# Initialization of the core object
plant_system = NuclearPlant()
# ==========================================
# [4] THE REACTOR SYSTEM (Thermal & Integrity)
# ==========================================
class ReactorCore:
    def __init__(self, plant):
        self.plant = plant
        self.temp = 20.0        # Ambient Temperature
        self.integrity = 100.0  # Percentage
        self.rods = 0           # Control Rods (0 to 100% out)
        self.meltdown_temp = 3000.0

    def calculate(self):
        # 1. Heat Generation: Higher rods = faster heat gain
        fission_heat = self.rods * 8.5
        
        # 2. Heat Dissipation: Based on Cooling System flow
        # If pumps are off (flow is 0), heat stays in the core
        coolant_effect = self.plant.cooling.flow_rate * 0.45
        
        # 3. Delta Temperature
        thermal_change = fission_heat - coolant_effect
        self.temp += thermal_change
        
        # Safety floor (Can't go below 20C)
        self.temp = max(20.0, self.temp)

        # 4. Integrity Decay
        if self.temp > 2500:
            self.integrity -= 2.0  # Rapid melting
        elif self.temp > 1800:
            self.integrity -= 0.5  # Structural stress

# ==========================================
# [5] THE COOLING LOOP (Hydraulics & Pumps)
# ==========================================
class CoolingSystem:
    def __init__(self, plant):
        self.plant = plant
        self.flow_rate = 0.0
        self.pumps_active = 0
        self.max_pumps = 4

    def calculate(self):
        # IMPORTANT: Pumps ONLY work if the Electrical Grid has power
        if self.plant.grid.has_power:
            self.flow_rate = self.pumps_active * 50.0
        else:
            self.flow_rate = 0.0

# ==========================================
# [6] THE ELECTRICAL BUS (Power Grid Logic)
# ==========================================
class PowerBus:
    def __init__(self, plant):
        self.plant = plant
        self.mode = "External" # Sources: External, Turbine, EOG
        self.has_power = True
        self.external_damaged = False
        
        # The Request/Approval Data Store
        self.pending_request = None # Dict: {"mode": str, "by": int}

    def calculate(self):
        # External: Government power (Safe but can be damaged)
        if self.mode == "External":
            self.has_power = not self.external_damaged
            
        # Turbine: Self-generated (Requires 3000 RPM sync)
        elif self.mode == "Turbine":
            if self.plant.turbines.rpm >= 2980:
                self.has_power = True
            else:
                self.has_power = False # Under-frequency trip
                
        # EOG: Emergency Generators (Always works but high fuel cost)
        elif self.mode == "EOG":
            self.has_power = True

# ==========================================
# [7] THE TURBINE SYSTEM (Steam Energy)
# ==========================================
class TurbineSystem:
    def __init__(self, plant):
        self.plant = plant
        self.rpm = 0.0
        self.throttle = 0 # 0 to 100% steam intake

    def calculate(self):
        # Steam pressure is generated when Core Temp > 100C
        steam_pressure = max(0, (self.plant.core.temp - 100) * 0.4)
        
        # RPM is affected by throttle and steam pressure
        if steam_pressure > 10:
            self.rpm += (steam_pressure * (self.throttle / 100))
        
        # Natural friction decay
        self.rpm -= 12.5
        
        # Hard limits
        self.rpm = max(0, min(3500, self.rpm))

# --- LINKING THE SYSTEMS BACK TO THE MASTER ---
plant_system.core = ReactorCore(plant_system)
plant_system.cooling = CoolingSystem(plant_system)
plant_system.grid = PowerBus(plant_system)
plant_system.turbines = TurbineSystem(plant_system)
      # ==========================================
# [8] THE LOGISTICS FLEET (Fuel & Repairs)
# ==========================================
class LogisticsSystem:
    def __init__(self, plant):
        self.plant = plant
        # Resource Stocks
        self.diesel_fuel = 10000.0   # Liters (For EOGs)
        self.spare_parts = 100       # Units (For Maintenance)
        self.uranium_rods = 20       # Spare rods
        
        # Fleet Status
        self.trucks_idle = 5         # Total 5 Heavy Transports
        self.trucks_on_mission = 0

    def dispatch_fuel_convoy(self):
        """Standard fuel run: Uses 1 truck for 5 minutes"""
        if self.trucks_idle > 0:
            self.trucks_idle -= 1
            self.trucks_on_mission += 1
            # Returns to inventory via heartbeat logic later
            return True
        return False

# ==========================================
# [9] SECURITY & FACILITY CLEARANCE
# ==========================================
class SecuritySystem:
    def __init__(self, plant):
        self.plant = plant
        self.lockdown_active = False
        self.intruder_alert = False
        self.mcr_secured = True
        self.threat_level = "GREEN" # GREEN, YELLOW, ORANGE, RED

    def update_threat_level(self):
        """Threat level changes based on plant stability"""
        if self.plant.core.integrity < 50:
            self.threat_level = "ORANGE"
        elif self.plant.core.integrity < 25 or self.plant.meltdown_active:
            self.threat_level = "RED"
        else:
            self.threat_level = "GREEN"

# --- LINKING THE SYSTEMS BACK TO THE MASTER ---
plant_system.logistics = LogisticsSystem(plant_system)
plant_system.security = SecuritySystem(plant_system)

# ==========================================
# [10] REPLIT/LOCAL DB HELPER (Optional Fix)
# ==========================================
# Ensures the JSON file is initialized if it doesn't exist
if not os.path.exists("facility_v3_data.json"):
    plant_system.db.save()
  # ==========================================
# [11] THE BOT CONTROLLER (Heartbeat & Events)
# ==========================================
class V3PlantBot(commands.Bot):
    def __init__(self, plant_obj):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.plant = plant_obj
        # Fixed channel ID for system alerts (Replace with your actual channel ID)
        self.alert_channel_id = 123456789012345678 

    async def setup_hook(self):
        """Initializes the simulation and registers / commands"""
        self.global_heartbeat.start()
        await self.tree.sync()
        print(f"☢️ V3 Slash Commands Registered & Heartbeat Initiated.")

    @tasks.loop(seconds=5)
    async def global_heartbeat(self):
        """Processes the entire facility physics and logic every 5s."""
        status = self.plant.tick()
        
        # Handle the BOOM
        if status == "BOOM":
            await self.trigger_catastrophe()
        
        # Periodic Database Auto-Save
        self.plant.db.save()

    async def trigger_catastrophe(self):
        """Logic for a total facility loss."""
        channel = self.get_channel(self.alert_channel_id)
        pd_id = None
        
        # 1. Automatic Firing of the Plant Director (The Pig Clause Protection)
        # We loop through all users to find the PD
        for uid, data in self.plant.db.data["users"].items():
            if data["rank"] == "Plant Director":
                pd_id = uid
                # The Reset: Wipe job/rank, SAVE XP.
                data["dept"] = "Unemployed"
                data["rank"] = "None"
                data["cooldown"] = int(time.time()) + 3600 # 1 Hour suspension
                break
        
        # 2. Reset the physical plant variables
        self.plant.core.temp = 20.0
        self.plant.core.integrity = 100.0
        self.plant.core.rods = 0
        self.plant.meltdown_active = False
        self.plant.db.data["global_stats"]["melt_count"] += 1
        
        # 3. Notification
        if channel:
            msg = "☢️ **CRITICAL ALERT: CORE MELTDOWN** ☢️\n"
            msg += "Reactor integrity reached 0%. The containment has failed.\n"
            if pd_id:
                msg += f"Plant Director <@{pd_id}> has been terminated for failure to maintain safety protocols."
            else:
                msg += "No Plant Director was identified as being on-shift."
            await channel.send(msg)

# --- INSTANTIATE THE BOT ---
bot = V3PlantBot(plant_system)

# ==========================================
# [12] UTILITY: AUTHENTICATION CHECK
# ==========================================
def has_clearance(interaction: discord.Interaction, required_dept: str):
    user_data = bot.plant.db.get_user(interaction.user.id)
    # PD and DOE have access to everything
    if user_data["rank"] in ["Plant Director", "Head of Department of Energy"]:
        return True
    return user_data["dept"] == required_dept
  # ==========================================
# [13] EMPLOYMENT & PROFILE COMMANDS
# ==========================================

@bot.tree.command(name="profile", description="View your facility ID, Rank, and archived XP")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    user_data = bot.plant.db.get_user(target.id)
    
    # Calculate current rank based on their XP and Dept
    current_rank = calculate_rank_from_xp(user_data["xp"], user_data["dept"])
    if user_data["dept"] == "Unemployed":
        current_rank = "No Active Contract"

    embed = discord.Embed(title="💳 PERSONNEL IDENTIFICATION", color=0x2f3136)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    embed.add_field(name="Employee", value=target.mention, inline=True)
    embed.add_field(name="Department", value=user_data["dept"], inline=True)
    embed.add_field(name="Current Rank", value=f"**{current_rank}**", inline=False)
    
    # Financials and Progress
    embed.add_field(name="Experience (XP)", value=f"📈 {user_data['xp']:,}", inline=True)
    embed.add_field(name="Wallet", value=f"💵 ${user_data['balance']:,}", inline=True)
    
    # Status Check (Handling the 1-hour cooldown)
    status = "✅ ACTIVE"
    if time.time() < user_data["cooldown"]:
        mins_remaining = int((user_data["cooldown"] - time.time()) / 60)
        status = f"🚫 BLACKLISTED ({mins_remaining}m)"
    
    embed.add_field(name="Duty Status", value=status, inline=False)
    embed.set_footer(text=f"ID: {target.id} | Facility V3 Security Protocol")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="apply", description="Apply for a position in a specific department")
@app_commands.describe(department="Choose: Operations, Maintenance, Security, Logistics, Corporate, Management")
async def apply(interaction: discord.Interaction, department: str):
    user_data = bot.plant.db.get_user(interaction.user.id)
    
    # 1. Cooldown/Blacklist Check
    if time.time() < user_data["cooldown"]:
        mins = int((user_data["cooldown"] - time.time()) / 60)
        return await interaction.response.send_message(f"❌ You are blacklisted from the facility for another {mins} minutes.", ephemeral=True)

    # 2. Check if already employed
    if user_data["dept"] != "Unemployed":
        return await interaction.response.send_message("❌ You are already employed! Resign or get fired first.", ephemeral=True)

    valid_depts = ["Operations", "Maintenance", "Security", "Logistics", "Corporate", "Management"]
    if department not in valid_depts:
        return await interaction.response.send_message(f"❌ Invalid Department. Choose from: {', '.join(valid_depts)}", ephemeral=True)

    # 3. Set Pending Status
    user_data["pending_dept"] = department
    bot.plant.db.save()
    
    await interaction.response.send_message(f"📝 Your application for the **{department}** department has been submitted for review.")

@bot.tree.command(name="hire", description="Hire a pending applicant (Shift Manager/PD Only)")
@app_commands.describe(member="The user to hire")
async def hire(interaction: discord.Interaction, member: discord.Member):
    executor = bot.plant.db.get_user(interaction.user.id)
    target = bot.plant.db.get_user(member.id)
    
    # Authority Check
    if executor["rank"] not in ["Shift Manager", "Plant Director"]:
        return await interaction.response.send_message("❌ Unauthorized: Only Management can hire personnel.", ephemeral=True)

    if not target["pending_dept"]:
        return await interaction.response.send_message(f"❌ {member.display_name} does not have a pending application.", ephemeral=True)

    # Execute Hiring
    target["dept"] = target["pending_dept"]
    target["pending_dept"] = None
    
    # Auto-calculate rank based on their archived XP
    target["rank"] = calculate_rank_from_xp(target["xp"], target["dept"])
    
    bot.plant.db.save()
    
    await interaction.response.send_message(f"🤝 {member.mention} has been hired into **{target['dept']}** as a **{target['rank']}**!")
  # ==========================================
# [14] AUTHORITY & DISCIPLINARY ACTIONS
# ==========================================

@bot.tree.command(name="fire", description="Terminate an employee's contract (XP and Balance are ARCHIVED)")
@app_commands.describe(member="The employee to terminate", reason="Reason for firing")
async def fire(interaction: discord.Interaction, member: discord.Member, reason: str):
    executor = bot.plant.db.get_user(interaction.user.id)
    target = bot.plant.db.get_user(member.id)
    
    # 1. Self-Fire Check
    if interaction.user.id == member.id:
        return await interaction.response.send_message("❌ You cannot fire yourself. Use `/resign`.", ephemeral=True)

    # 2. Hierarchy Check
    # Plant Director (PD) is top tier, but DOE is the Government.
    if executor["rank"] == "Plant Director":
        if "Department of Energy" in target["rank"]:
            return await interaction.response.send_message("❌ Error: You cannot fire Government Oversight (DOE).", ephemeral=True)
    
    # Shift Managers have limited power
    elif executor["rank"] == "Shift Manager":
        if target["dept"] == "Corporate":
            return await interaction.response.send_message("❌ Error: Shift Managers lack authority over Corporate staff.", ephemeral=True)
        if target["rank"] in ["Plant Director", "Shift Manager"] or "Head of" in target["rank"]:
            return await interaction.response.send_message("❌ Error: You cannot fire your equals or superiors.", ephemeral=True)
    
    else:
        return await interaction.response.send_message("❌ Unauthorized: Only Shift Managers or the PD can fire staff.", ephemeral=True)

    # 3. Execution of "The Pig Clause"
    # We clear the job data but KEEP the XP and Balance fields.
    target["dept"] = "Unemployed"
    target["rank"] = "None"
    target["pending_dept"] = None
    target["cooldown"] = int(time.time()) + 3600 # 1 Hour suspension
    
    bot.plant.db.save()
    
    embed = discord.Embed(title="📉 TERMINATION OF CONTRACT", color=0xff0000)
    embed.add_field(name="Terminated Employee", value=member.mention, inline=True)
    embed.add_field(name="Authorized By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text="Notice: Employee progress has been archived. 60m facility lockout active.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="promote", description="Manually promote a worker who meets XP requirements")
@app_commands.describe(member="The worker to promote")
async def promote(interaction: discord.Interaction, member: discord.Member):
    executor = bot.plant.db.get_user(interaction.user.id)
    target = bot.plant.db.get_user(member.id)
    
    if executor["rank"] not in ["Shift Manager", "Plant Director"]:
        return await interaction.response.send_message("❌ Only Management can authorize promotions.", ephemeral=True)

    # Check if they actually qualify for a new rank
    current_rank = target["rank"]
    qualified_rank = calculate_rank_from_xp(target["xp"], target["dept"])
    
    if current_rank == qualified_rank:
        return await interaction.response.send_message(f"❌ {member.display_name} does not have enough XP for a promotion yet.", ephemeral=True)

    # Execute Promotion
    target["rank"] = qualified_rank
    bot.plant.db.save()
    
    await interaction.response.send_message(f"🎊 **PROMOTION**: {member.mention} has been officially promoted to **{qualified_rank}**!")

@bot.tree.command(name="resign", description="Resign from your current position")
async def resign(interaction: discord.Interaction):
    user_data = bot.plant.db.get_user(interaction.user.id)
    
    if user_data["dept"] == "Unemployed":
        return await interaction.response.send_message("❌ You are not currently employed.", ephemeral=True)

    user_data["dept"] = "Unemployed"
    user_data["rank"] = "None"
    # No cooldown for resigning voluntarily
    bot.plant.db.save()
    
    await interaction.response.send_message("👋 You have resigned from your position. Your XP remains saved.")
  # ==========================================
# [15] THE MCR DASHBOARD (Global Overview)
# ==========================================

@bot.tree.command(name="mcr", description="Display the high-level facility status dashboard")
async def mcr(interaction: discord.Interaction):
    p = bot.plant
    
    # Dynamic Color based on Safety
    embed_color = 0x00ff00 # Green
    if p.core.temp > 1500: embed_color = 0xffa500 # Orange
    if p.core.temp > 2500 or p.core.integrity < 40: embed_color = 0xff0000 # Red

    embed = discord.Embed(title="☢️ MAIN CONTROL ROOM - SYSTEM SUMMARY", color=embed_color)
    
    # Column 1: Core & Physics
    core_status = f"🌡️ **Temp:** {round(p.core.temp, 1)}°C\n"
    core_status += f"🛠️ **Integrity:** {round(p.core.integrity, 1)}%\n"
    core_status += f"📊 **Rods:** {p.core.rods}% OUT"
    embed.add_field(name="REACTOR STATE", value=core_status, inline=True)
    
    # Column 2: Cooling & Steam
    cool_status = f"🌊 **Flow:** {p.cooling.flow_rate} L/s\n"
    cool_status += f"⚙️ **Pumps:** {p.cooling.pumps_active}/4\n"
    cool_status += f"🌀 **Turbine:** {int(p.turbines.rpm)} RPM"
    embed.add_field(name="THERMALS", value=cool_status, inline=True)
    
    # Column 3: Grid & Resources
    grid_status = f"🔌 **Source:** {p.grid.mode}\n"
    grid_status += f"⚡ **Bus:** {'✅ ONLINE' if p.grid.has_power else '❌ BLACKOUT'}\n"
    grid_status += f"🚛 **Trucks:** {p.logistics.trucks_idle} IDLE"
    embed.add_field(name="FACILITY BUS", value=grid_status, inline=True)

    embed.set_footer(text=f"Facility Status: {p.status} | Security Level: {p.security.threat_level}")
    await interaction.response.send_message(embed=embed)

# ==========================================
# [16] OPERATIONS PANEL (Rods & Turbines)
# ==========================================

class OpsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="RODS OUT 10%", style=discord.ButtonStyle.danger)
    async def rods_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_clearance(interaction, "Operations"):
            return await interaction.response.send_message("❌ Ops Clearance Required.", ephemeral=True)
        bot.plant.core.rods = min(100, bot.plant.core.rods + 10)
        await interaction.response.send_message(f"🔼 Rods pulled to {bot.plant.core.rods}%", ephemeral=True)

    @discord.ui.button(label="RODS IN 10%", style=discord.ButtonStyle.success)
    async def rods_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_clearance(interaction, "Operations"):
            return await interaction.response.send_message("❌ Ops Clearance Required.", ephemeral=True)
        bot.plant.core.rods = max(0, bot.plant.core.rods - 10)
        await interaction.response.send_message(f"🔽 Rods inserted to {bot.plant.core.rods}%", ephemeral=True)

@bot.tree.command(name="ops_panel", description="Operations: Manage Reactor Rods and Steam")
async def ops_panel(interaction: discord.Interaction):
    if not has_clearance(interaction, "Operations"):
        return await interaction.response.send_message("❌ Access Denied: Operations Department Only.", ephemeral=True)
    await interaction.response.send_message("🕹️ **REACTOR CONTROL CONSOLE**", view=OpsView())

# ==========================================
# [17] MAINTENANCE PANEL (The 4 Pumps)
# ==========================================

class MaintView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="START 1 PUMP", style=discord.ButtonStyle.primary)
    async def pump_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_clearance(interaction, "Maintenance"):
            return await interaction.response.send_message("❌ Maintenance Clearance Required.", ephemeral=True)
        if bot.plant.cooling.pumps_active < 4:
            bot.plant.cooling.pumps_active += 1
            await interaction.response.send_message(f"🌊 Pump started. Active: {bot.plant.cooling.pumps_active}/4", ephemeral=True)
        else:
            await interaction.response.send_message("❌ All pumps already active.", ephemeral=True)

    @discord.ui.button(label="STOP 1 PUMP", style=discord.ButtonStyle.secondary)
    async def pump_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_clearance(interaction, "Maintenance"):
            return await interaction.response.send_message("❌ Maintenance Clearance Required.", ephemeral=True)
        if bot.plant.cooling.pumps_active > 0:
            bot.plant.cooling.pumps_active -= 1
            await interaction.response.send_message(f"🛑 Pump stopped. Active: {bot.plant.cooling.pumps_active}/4", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No pumps running.", ephemeral=True)

@bot.tree.command(name="maint_panel", description="Maintenance: Control Cooling Pumps")
async def maint_panel(interaction: discord.Interaction):
    if not has_clearance(interaction, "Maintenance"):
        return await interaction.response.send_message("❌ Access Denied: Maintenance Department Only.", ephemeral=True)
    await interaction.response.send_message("🔧 **COOLING SYSTEM INTERFACE**", view=MaintView())
  # ==========================================
# [18] ELECTRICAL PANEL (EOGs & Grid Mode)
# ==========================================

class ElectricalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ACTIVATE EOG (Diesel)", style=discord.ButtonStyle.danger)
    async def activate_eog(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_clearance(interaction, "Maintenance"):
            return await interaction.response.send_message("❌ Maintenance/Ops Clearance Required.", ephemeral=True)
        
        # Check Fuel from Logistics
        if bot.plant.logistics.diesel_fuel >= 500:
            bot.plant.grid.mode = "EOG"
            bot.plant.logistics.diesel_fuel -= 500
            await interaction.response.send_message("⚡ Emergency Diesel Generators Online. Grid Source: EOG.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Insufficient Diesel Fuel! Call Logistics.", ephemeral=True)

    @discord.ui.button(label="SYNC TURBINE TO GRID", style=discord.ButtonStyle.primary)
    async def sync_turbine(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_clearance(interaction, "Operations"):
            return await interaction.response.send_message("❌ Operations Clearance Required.", ephemeral=True)
        
        if bot.plant.turbines.rpm >= 2950:
            bot.plant.grid.mode = "Turbine"
            await interaction.response.send_message("✅ Turbine Synced. The plant is now self-powering.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Sync Failed. RPM too low ({int(bot.plant.turbines.rpm)}/2950).", ephemeral=True)

@bot.tree.command(name="grid_panel", description="Electrical: Manage the Facility Power Bus")
async def grid_panel(interaction: discord.Interaction):
    if not has_clearance(interaction, "Maintenance") and not has_clearance(interaction, "Operations"):
        return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
    
    embed = discord.Embed(title="⚡ ELECTRICAL DISTRIBUTION PANEL", color=0xf1c40f)
    embed.add_field(name="Current Source", value=bot.plant.grid.mode)
    embed.add_field(name="Bus Stability", value="ONLINE" if bot.plant.grid.has_power else "OFFLINE")
    await interaction.response.send_message(embed=embed, view=ElectricalView())

# ==========================================
# [19] LOGISTICS PANEL (Fuel & Supply Chains)
# ==========================================

class LogisticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="DISPATCH FUEL CONVOY", style=discord.ButtonStyle.success)
    async def fuel_convoy(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_clearance(interaction, "Logistics"):
            return await interaction.response.send_message("❌ Logistics Clearance Required.", ephemeral=True)
        
        if bot.plant.logistics.trucks_idle > 0:
            bot.plant.logistics.trucks_idle -= 1
            # Simulate a 10-second delivery for the game
            await interaction.response.send_message("🚛 Convoy dispatched. Fuel arriving in 10 seconds...", ephemeral=True)
            await asyncio.sleep(10)
            bot.plant.logistics.diesel_fuel += 2500
            bot.plant.logistics.trucks_idle += 1
            await interaction.followup.send("📦 Fuel Delivered: +2500L Diesel added to stockpile.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No trucks available in the fleet.", ephemeral=True)

@bot.tree.command(name="logistics_panel", description="Logistics: Manage Fleet and Supplies")
async def logistics_panel(interaction: discord.Interaction):
    if not has_clearance(interaction, "Logistics"):
        return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
    
    l = bot.plant.logistics
    embed = discord.Embed(title="🚛 LOGISTICS & SUPPLY DEPOT", color=0x3498db)
    embed.add_field(name="Diesel Stock", value=f"{l.diesel_fuel}L")
    embed.add_field(name="Idle Trucks", value=f"{l.trucks_idle}/5")
    await interaction.response.send_message(embed=embed, view=LogisticsView())

# ==========================================
# [20] THE WORK COMMAND (XP & Promotion Loop)
# ==========================================

@bot.tree.command(name="work", description="Perform your duties to earn XP and Money")
async def work(interaction: discord.Interaction):
    user_data = bot.plant.db.get_user(interaction.user.id)
    dept = user_data["dept"]

    if dept == "Unemployed":
        return await interaction.response.send_message("❌ You aren't employed! Use `/apply`.", ephemeral=True)

    # Reward scaling based on Dept
    xp_gain = 100 if dept == "Management" else 60
    pay = 500 if dept == "Management" else 250

    user_data["xp"] += xp_gain
    user_data["balance"] += pay
    
    # Auto-Promotion Check
    new_rank = calculate_rank_from_xp(user_data["xp"], dept)
    if new_rank != user_data["rank"]:
        user_data["rank"] = new_rank
        await interaction.channel.send(f"🎊 **PROMOTION**: {interaction.user.mention} is now a **{new_rank}**!")
    
    bot.plant.db.save()
    await interaction.response.send_message(f"✅ Duty complete! You earned **{xp_gain} XP** and **${pay}**.")

# ==========================================
# [21] THE FINAL STARTUP
# ==========================================
# Replace 'YOUR_BOT_TOKEN' with the actual token.
# bot.run("YOUR_BOT_TOKEN")

  
