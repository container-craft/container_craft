
## Keep in mind that this will be in C at some point. No need to load json or whatever. This is just
## quick and helps us move forward on testing the framework for
CODENAME_TO_VERSIONS = {}
MC_CODENAMES = {
    # 1.21
    "1.21.8": "tricky_trials",
    "1.21.7": "tricky_trials",
    "1.21.6": "tricky_trials",
    "1.21.5": "tricky_trials",
    "1.21.4": "tricky_trials",
    "1.21.3": "tricky_trials",
    "1.21.2": "tricky_trials",
    "1.21.1": "tricky_trials",
    "1.21":   "tricky_trials",

    # 1.20
    "1.20.6": "trails_and_tales",
    "1.20.5": "trails_and_tales",
    "1.20.4": "trails_and_tales",
    "1.20.3": "trails_and_tales",
    "1.20.2": "trails_and_tales",
    "1.20.1": "trails_and_tales",
    "1.20":   "trails_and_tales",

    # 1.19
    "1.19.4": "the_wild",
    "1.19.3": "the_wild",
    "1.19.2": "the_wild",
    "1.19.1": "the_wild",
    "1.19":   "the_wild",

    # 1.18
    "1.18.2": "caves_and_cliffs_two",
    "1.18.1": "caves_and_cliffs_two",
    "1.18":   "caves_and_cliffs_two",

    # 1.17
    "1.17.1": "caves_and_cliffs_one",
    "1.17":   "caves_and_cliffs_one",

    # 1.16
    "1.16.5": "nether_update",
    "1.16.4": "nether_update",
    "1.16.3": "nether_update",
    "1.16.2": "nether_update",
    "1.16.1": "nether_update",
    "1.16":   "nether_update",

     # 1.15
    "1.15.2": "buzzy_bees",
    "1.15.1": "buzzy_bees",
    "1.15":   "buzzy_bees",

    # 1.14
    "1.14.4": "village_and_pillage",
    "1.14.3": "village_and_pillage",
    "1.14.2": "village_and_pillage",
    "1.14.1": "village_and_pillage",
    "1.14":   "village_and_pillage",

    # 1.13
    "1.13.2": "aquatic",
    "1.13.1": "aquatic",
    "1.13":   "aquatic",

    # 1.12
    "1.12.2": "world_of_color",
    "1.12.1": "world_of_color",
    "1.12":   "world_of_color",

    # 1.11
    "1.11.2": "exploration",
    "1.11.1": "exploration",
    "1.11":   "exploration",

    # 1.10
    "1.10.2": "frostburn",
    "1.10.1": "frostburn",
    "1.10":   "frostburn",

    # 1.9
    "1.8.4": "combat",
    "1.8.3": "combat",
    "1.8.2": "combat",
    "1.8.1": "combat",
    "1.8":   "combat",

    # 1.8
    "1.8.8": "bountiful",
    "1.8.8": "bountiful",
    "1.8.7": "bountiful",
    "1.8.6": "bountiful",
    "1.8.5": "bountiful",
    "1.8.4": "bountiful",
    "1.8.3": "bountiful",
    "1.8.2": "bountiful",
    "1.8.1": "bountiful",
    "1.8":   "bountiful",

    # 1.7
    "1.7.10": "changed_the_world",
    "1.7.9":  "changed_the_world",
    "1.7.8":  "changed_the_world",
    "1.7.7":  "changed_the_world",
    "1.7.6":  "changed_the_world",
    "1.7.5":  "changed_the_world",
    "1.7.4":  "changed_the_world",
    "1.7.2":  "changed_the_world",

    # 1.6
    "1.6.4": "horse",
    "1.6.2": "horse",
    "1.6.1": "horse",

    # 1.5
    "1.5.2": "redstone",
    "1.5.1": "redstone",
    "1.5":   "redstone",

    # 1.4(ODD on the release numbers :/)
    "1.4.7": "pretty_scary",
    "1.4.6": "pretty_scary",
    "1.4.5": "pretty_scary",
    "1.4.4": "pretty_scary",
    "1.4.3": "pretty_scary",
    "1.4.2": "pretty_scary",

    # 1.3
    "1.3.2": "villager_trading",
    "1.3.1": "villager_trading",

    # 1.2
    "1.2.5": "faithful",
    "1.2.4": "faithful",
    "1.2.3": "faithful",
    "1.2.2": "faithful",
    "1.2.1": "faithful",

    # 1.1
    "1.1":   "spawn_egg",

    # 1.0
    "1.0.1": "adventure",
    "1.0":   "adventure",

    # I'm not doing beta
}

for ver, code in MC_CODENAMES.items():
    CODENAME_TO_VERSIONS.setdefault(code, []).append(ver)

def versions(code_name: str) -> list[str]:
    """Return a list of versions for a given codename."""
    return CODENAME_TO_VERSIONS.get(code_name, [])

def latest_version(code_name: str) -> str:
    ver = versions(code_name)
    if not ver:
        return None
    return sorted(ver, key=lambda v: [int(x) for x in v.split('.')])[-1]

def codename(mc_version: str) -> str:
    return MC_CODENAMES.get(mc_version)
