# Function Categorization Plan

## 📊 Summary
- **Total unused functions**: 98
- **Files with unused functions**: 22
- **Functions to COMMENT OUT**: 95 (planned features)
- **Functions to REMOVE**: 3 (truly unnecessary)

## 🎯 Categorization Results

### 💬 **COMMENT OUT - Planned Features (95 functions)**

#### **Public API Functions (Getter/Setter/Query functions)**
These are all planned public API functions for future UI, debugging, and system integration:

**GameManager.gd (7 functions)**
- `complete_game()` - Game completion logic
- `new_game()` - New game functionality  
- `get_game_state()` - Game state queries
- `is_game_playing()` - Game state queries
- `is_game_completed()` - Game state queries
- `get_game_progress()` - Progress tracking
- `get_game_info()` - Game information

**TimeManager.gd (5 functions)**
- `get_available_time_speeds()` - Time control UI
- `get_day_night_progress()` - Day/night cycle display
- `get_work_hours_progress()` - Work hours display
- `set_work_hours()` - Work hours configuration
- `get_work_hours()` - Work hours queries

**MultiplierManager.gd (13 functions)**
- All getter/setter functions for multiplier data
- Planned for UI displays and debug tools

**ResourceManager.gd (9 functions)**
- `is_valid_resource_name()` - Resource validation utility
- `register_resource_tick()` - Resource tick system
- `set_mana()` - Mana management
- `toggle_daily_collection()` - Collection system
- `set_daily_collection_enabled()` - Collection system
- `_on_food_consumption_tick()` - Food consumption system
- `_on_upkeep_tick()` - Upkeep system
- `get_available_building_slots()` - Building slot queries
- `set_all_resources()` - Resource management

**EventManager.gd (7 functions)**
- `trigger_custom_event()` - Custom event system
- `schedule_event()` - Event scheduling
- `schedule_daily_event()` - Daily event system
- `get_current_events()` - Event queries
- `clear_event()` - Event management
- `get_scheduled_events()` - Event queries
- `is_event_scheduled()` - Event queries

**SpellManager.gd (4 functions)**
- `get_spell_remaining_duration()` - Spell duration queries
- `get_spell_progress()` - Spell progress display
- `get_spell_mana_cost()` - Spell cost queries
- `get_spells_by_effect_type()` - Spell queries

**UnlockManager.gd (1 function)**
- `get_unlocked_items()` - Unlock status queries

**PopulationCrisisManager.gd (4 functions)**
- `resolve_crisis()` - Crisis resolution
- `get_active_crises()` - Crisis queries
- `set_crisis_threshold()` - Crisis configuration
- `get_crisis_config()` - Crisis configuration

**PopulationManager.gd (4 functions)**
- `check_for_crises()` - Crisis checking
- `_on_population_capacity_changed()` - Population capacity events
- `_on_population_crisis_triggered()` - Crisis events
- `_on_crisis_warning()` - Crisis warning events

**PopulationStateManager.gd (3 functions)**
- `get_population_growth_rate()` - Growth rate queries
- `get_housing_status()` - Housing status queries
- `get_population_summary()` - Population summary

**DataManager.gd (8 functions)**
- `_process_buildings_data()` - Data processing
- `_process_jobs_data()` - Data processing
- `_process_effects_data()` - Data processing
- `set_selected_origin()` - Origin management
- `get_upgrade_data()` - Upgrade data queries
- `get_origin_data()` - Origin data queries
- `get_all_upgrades()` - Upgrade queries
- `get_event_data()` - Event data queries

**SaveLoadManager.gd (4 functions)**
- `save_game()` - Save functionality
- `load_game()` - Load functionality
- `delete_save()` - Save management
- `backup_save()` - Save management

**PopupManager.gd (3 functions)**
- `_on_event_choice_made()` - Event choice events
- `_on_event_popup_closed()` - Popup events
- `get_popup_instance()` - Popup queries

**ResearchBarManager.gd (3 functions)**
- `get_current_research_info()` - Research info queries
- `is_displaying_research()` - Research display queries
- `reset_research_bar()` - Research bar management

**TooltipManager.gd (3 functions)**
- `is_tooltip_visible()` - Tooltip visibility queries
- `get_current_tooltip()` - Tooltip queries
- `clear_tooltip()` - Tooltip management

**ResearchManager.gd (2 functions)**
- `get_research_level()` - Research level queries
- `cancel_research()` - Research cancellation

**UpgradeTypeManager.gd (6 functions)**
- `get_researched_for_type()` - Research queries
- `get_data_for_type()` - Data queries
- `start_research_for_type()` - Research management
- `get_all_upgrade_types()` - Upgrade type queries
- `get_total_researched_count()` - Research count queries
- `get_research_summary()` - Research summary

**ProductionCalculatorManager.gd (3 functions)**
- `get_daily_production_accumulation()` - Production queries
- `get_daily_collection_jobs()` - Job queries
- `get_continuous_collection_jobs()` - Job queries

**WorkerEfficiencyManager.gd (3 functions)**
- `set_worker_efficiency()` - Efficiency management
- `get_building_worker_summary()` - Worker summary queries
- `get_worker_distribution()` - Worker distribution queries

**WorkerManager.gd (2 functions)**
- `get_job_types()` - Job type queries
- `set_all_workers()` - Worker management

**MapManager.gd (1 function)**
- `has_free_capacity()` - Tile capacity checking (already commented out)

### ✅ **KEEP - Useful Utilities (3 functions)**

**version_manager.gd (3 functions)**
- `get_version()` - Simple getter, useful utility
- `is_stable_release()` - Version checking utility  
- `print_version_info()` - Debug/development utility

## 🎯 **Action Plan**

### **Phase 1: Comment Out Planned Features (95 functions)**
- Use consistent commenting pattern
- Add clear markers: `# PLANNED FEATURE - COMMENTED OUT`
- Move to bottom of file or group together
- Add TODO comments for future implementation

### **Phase 2: Keep Useful Utilities (3 functions)**
- Leave version_manager.gd functions as-is
- They're useful utilities that might be used

### **Phase 3: Verify Clean Codebase**
- Run audit again to confirm all unused functions are handled
- Ensure no functionality is broken

## 📝 **Commenting Pattern**
```gdscript
# =============================================================================
# PLANNED FEATURES - COMMENTED OUT
# =============================================================================
# TODO: Uncomment these functions when implementing the planned feature system
# These functions are ready to use but not currently needed in the game

# func function_name() -> ReturnType:
# 	"""Function description - PLANNED FEATURE"""
# 	# Implementation details
# 	pass
```

## 🚀 **Benefits**
- **Clean current codebase** - No unused function warnings
- **Preserve planned features** - Code ready for future implementation
- **Clear documentation** - Easy to find and uncomment when needed
- **No functionality loss** - All planned features preserved
- **Consistent pattern** - Easy to maintain and understand
