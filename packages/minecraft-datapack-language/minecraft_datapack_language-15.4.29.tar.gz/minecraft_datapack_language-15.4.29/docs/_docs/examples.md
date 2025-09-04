---
layout: page
title: MDL Examples
permalink: /docs/examples/
---

This page contains working examples of MDL features.

## Basic Hello World

A simple datapack that says hello when loaded:

```mdl
pack "hello" "A simple hello world datapack" 82;
namespace "hello";

function "main" {
    say Hello, Minecraft!;
    tellraw @a {"text":"Welcome to my datapack!","color":"green"};
}

on_load "hello:main";
```

## Counter with Scoped Variables

Demonstrates variables with different scopes:

```mdl
pack "counter" "Counter example" 82;
namespace "counter";

var num globalCounter scope<global> = 0;
var num playerCounter = 0;  // Defaults to player-specific scope

function "increment" {
    globalCounter<global> = globalCounter<global> + 1;
    playerCounter<@s> = playerCounter<@s> + 1;
    say Global: $globalCounter$, Player: $playerCounter$;
}

function "show_all" {
    function "counter:increment<@a>";
}

on_load "counter:increment";
```

## While Loop Example

A countdown timer using a while loop:

```mdl
pack "loops" "Loop example" 82;
namespace "loops";

var num counter scope<global> = 0;

function "countdown" {
    counter<global> = 5;
    while "$counter$ > 0" {
        say Countdown: $counter$;
        counter<global> = counter<global> - 1;
    }
    say Blast off!;
}

on_load "loops:countdown";
```

## Raw Commands

Using raw Minecraft commands:

```mdl
pack "raw" "Raw command example" 82;
namespace "raw";

function "custom" {
    // Use raw Minecraft commands
    effect give @s minecraft:speed 10 1;
    particle minecraft:explosion ~ ~ ~ 1 1 1 0 10;
    playsound minecraft:entity.player.levelup player @s ~ ~ ~ 1 1;
}

on_load "raw:custom";
```

## Complete Game Example

A complete game with scoring, levels, and timers:

```mdl
pack "game" "Complete game example" 82;
namespace "game";

// Variables
var num score = 0;  // Defaults to player-specific scope
var num level = 1;  // Defaults to player-specific scope
var num globalTimer scope<global> = 0;

// Main game function
function "start_game" {
    score<@s> = 0;
    level<@s> = 1;
    say Game started! Level: $level$, Score: $score$;
}

// Level up function
function "level_up" {
    if "$score$ >= 100" {
        level<@s> = level<@s> + 1;
        score<@s> = score<@s> - 100;
        say Level up! New level: $level$;
        tellraw @a {"text":"Player leveled up!","color":"gold"};
    }
}

// Timer function
function "update_timer" {
    globalTimer<global> = globalTimer<global> + 1;
    if "$globalTimer$ >= 1200" {  // 60 seconds
        globalTimer<global> = 0;
        say Time's up! Final score: $score$;
    }
}

// Add score function
function "add_score" {
    score<@s> = score<@s> + 10;
    say Score: $score$;
    function "game:level_up";
}

// Hooks
on_load "game:start_game";
on_tick "game:update_timer";
```

## Team-Based System

A system that tracks team scores:

```mdl
pack "teams" "Team system example" 82;
namespace "teams";

// Team variables
var num redScore scope<@a[team=red]> = 0;
var num blueScore scope<@a[team=blue]> = 0;
var num gameTimer scope<global> = 0;

// Initialize teams
function "init" {
    redScore<@a[team=red]> = 0;
    blueScore<@a[team=blue]> = 0;
    gameTimer<global> = 0;
    say Team game initialized!;
}

// Update game
function "update" {
    gameTimer<global> = gameTimer<global> + 1;
    
    if "$gameTimer$ >= 2400" {  // 2 minutes
        gameTimer<global> = 0;
        say Game over! Red: $redScore$, Blue: $blueScore$;
        
        if "$redScore$ > $blueScore$" {
            tellraw @a {"text":"Red team wins!","color":"red"};
        } else if "$blueScore$ > $redScore$" {
            tellraw @a {"text":"Blue team wins!","color":"blue"};
        } else {
            tellraw @a {"text":"It's a tie!","color":"yellow"};
        }
    }
}

// Add points to red team
function "red_point" {
    redScore<@a[team=red]> = redScore<@a[team=red]> + 1;
    say Red team score: $redScore$;
}

// Add points to blue team
function "blue_point" {
    blueScore<@a[team=blue]> = blueScore<@a[team=blue]> + 1;
    say Blue team score: $blueScore$;
}

// Hooks
on_load "teams:init";
on_tick "teams:update";
```

## Multi-File Example

Organizing code across multiple files:

**`main.mdl`** (with pack declaration):
```mdl
pack "multifile" "Multi-file example" 82;
namespace "core";

var num playerCount scope<global> = 0;

function "init" {
    playerCount = 0;
    say Core system initialized!;
}

on_load "core:init";
```

**`ui.mdl`** (no pack declaration needed):
```mdl
namespace "ui";

function "show_hud" {
    tellraw @a {"text":"Players: $playerCount$","color":"green"};
}

function "update_hud" {
    function "ui:show_hud<@a>";
}
```

**`game.mdl`** (no pack declaration needed):
```mdl
namespace "game";

function "start" {
    say Game started!;
    function "ui:update_hud";
}
```

Build all files together:
```bash
mdl build --mdl "main.mdl ui.mdl game.mdl" -o dist
```

## Explicit Scopes in Conditions

Demonstrates how to use explicit scope selectors in if/while conditions to override declared variable scopes:

```mdl
pack "scopes" "Explicit scope conditions example" 82;
namespace "scopes";

// Variables with different scopes
var num playerScore = 0;                    // Defaults to @s
var num globalCounter scope<global> = 0;    // Global scope
var num teamScore scope<@a[team=red]> = 0;  // Team scope

function "main" {
    // Test explicit scope overrides in if conditions
    if "$playerScore<@s>$ > 10" {
        say "Current player score is high!";
    }
    
    if "$globalCounter<global>$ > 100" {
        say "Global counter reached milestone!";
    }
    
    if "$teamScore<@a[team=red]>$ > 50" {
        say "Red team is winning!";
    }
    
    // Check another player's score
    if "$playerScore<@p[name=Steve]>$ > 5" {
        say "Steve has a good score!";
    }
    
    // Check if any player has a high score
    if "$playerScore<@a>$ > 20" {
        say "Someone has a very high score!";
    }
    
    // Use explicit scopes in while loops too
    while "$globalCounter<global>$ < 10" {
        globalCounter<global> = globalCounter<global> + 1;
        say "Counter: $globalCounter$";
    }
}

// Function to test different scopes
function "test_scopes" {
    // Set different values for different scopes
    playerScore<@s> = 15;                    // Current player
    globalCounter<global> = 150;             // Global
    teamScore<@a[team=red]> = 75;           // Red team
    
    // Test conditions with explicit scopes
    if "$playerScore<@s>$ > 10" {
        say "Player score check passed!";
    }
    
    if "$globalCounter<global>$ > 100" {
        say "Global counter check passed!";
    }
    
    if "$teamScore<@a[team=red]>$ > 50" {
        say "Team score check passed!";
    }
}

on_load "scopes:main";
```

**Key Features:**
- **Override declared scopes**: Use `<@s>`, `<global>`, `<@a[team=red]>` in conditions
- **Check other entities**: Compare scores across different players/teams
- **Flexible conditions**: Mix and match scopes as needed
- **Clear intent**: Explicit scope makes code more readable and debuggable


