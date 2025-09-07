#!/bin/bash
#
# bump.sh
#
# A shell script for parsing a Python comment string that contains versioning
# metdata, incrementing its build number, and writing the updated value back
# to the the package's `__init__.py`.
#
set -e  # Exit on any error

VERSION_FILE="src/starch/constants.py"

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Please install jq first."
    echo "On macOS: brew install jq"
    echo "On Ubuntu/Debian: sudo apt-get install jq"
    exit 1
fi

# Check if init file exists
if [[ ! -f "$VERSION_FILE" ]]; then
    echo "Error: $VERSION_FILE not found"
    exit 1
fi

# Extract version config JSON from the file
get_version_config() {
    local key="$1"
    grep "VERSION_CONFIG:" "$VERSION_FILE" | \
        sed 's/.*VERSION_CONFIG: //' | \
        jq -r "$key"
}

# Update the JSON config line in the file
update_config_line() {
    local new_config="$1"
    # Use a temporary file for safer replacement
    local temp_file
    temp_file=$(mktemp)
    
    # Use awk to safely replace the VERSION_CONFIG line
    awk -v new_config="$new_config" '
        /VERSION_CONFIG:/ { 
            print "# VERSION_CONFIG: " new_config
            next 
        }
        { print }
    ' "$VERSION_FILE" > "$temp_file"
    
    mv "$temp_file" "$VERSION_FILE"
}

# Generate version string from components
generate_version_string() {
    local base="$1"
    local phase="$2"
    local build="$3"
    
    if [[ "$phase" == "" || "$phase" == "null" ]]; then
        echo "$base"
    else
        echo "${base}${phase}${build}"
    fi
}

# Update the __version__ line in the file
update_version_line() {
    local new_version="$1"

    # Use a temporary file for safer replacement
    local temp_file
    temp_file=$(mktemp)

    sed "s|__version__ = \".*\"|__version__ = \"$new_version\"|" "$VERSION_FILE" > "$temp_file"
    mv "$temp_file" "$VERSION_FILE"
}

# Update both config and version lines
sync_version() {
    local base
    base=$(get_version_config '.base')

    local phase
    phase=$(get_version_config '.phase')

    local build
    build=$(get_version_config '.build')
    
    local new_version
    new_version=$(generate_version_string "$base" "$phase" "$build")

    update_version_line "$new_version"
}

# Show current version information
show_current() {
    local base
    base=$(get_version_config '.base')

    local phase
    phase=$(get_version_config '.phase')

    local build
    build=$(get_version_config '.build')

    local current_version
    current_version=$(grep '__version__ = ' "$VERSION_FILE" | sed 's/.*"\(.*\)".*/\1/')
    
    echo "Base: $base"
    echo "Phase: ${phase:-"(final)"}"
    echo "Build: $build"
    echo "Current version: $current_version"
}

# Bump build number
bump_build() {
    local current_build
    current_build=$(get_version_config '.build')
    local new_build=$((current_build + 1))
    
    # Update JSON config
    local current_config
    current_config=$(grep "VERSION_CONFIG:" "$VERSION_FILE" | sed 's/.*VERSION_CONFIG: //')

    local new_config
    new_config=$(echo "$current_config" | jq -c ".build = $new_build")  # Add -c flag here
    
    update_config_line "$new_config"
    sync_version
    
    echo "Bumped build from $current_build to $new_build"
}

# Set development phase
set_phase() {
    local phase="$1"
    
    # Convert "final" to empty string for JSON
    if [[ "$phase" == "final" ]]; then
        phase=""
    fi
    
    # Validate phase
    if [[ "$phase" != "" && "$phase" != "a" && "$phase" != "b" && "$phase" != "rc" ]]; then
        echo "Error: Phase must be one of: a, b, rc, final"
        exit 1
    fi
    
    # Update JSON config
    local current_config
    current_config=$(grep "VERSION_CONFIG:" "$VERSION_FILE" | sed 's/.*VERSION_CONFIG: //')
    local new_config
    new_config=$(echo "$current_config" | jq -c ".phase = \"$phase\"")  # Add -c flag here
    
    update_config_line "$new_config"
    sync_version
    
    if [[ "$phase" == "" ]]; then
        echo "Set phase to: final"
    else
        echo "Set phase to: $phase"
    fi
}

# Set base version
set_base() {
    local base="$1"
    
    # Basic validation for semantic version format
    if [[ ! "$base" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Base version must be in format x.y.z (e.g., 1.0.0)"
        exit 1
    fi
    
    # Update JSON config
    local current_config
    current_config=$(grep "VERSION_CONFIG:" "$VERSION_FILE" | sed 's/.*VERSION_CONFIG: //')

    local new_config
    new_config=$(echo "$current_config" | jq -c ".base = \"$base\"")  # Add -c flag here
    
    update_config_line "$new_config"
    sync_version
    
    echo "Set base version to: $base"
}

# Reset to alpha.1
reset_phase() {
    local current_config
    current_config=$(grep "VERSION_CONFIG:" "$VERSION_FILE" | sed 's/.*VERSION_CONFIG: //')

    local new_config
    new_config=$(echo "$current_config" | jq -c '.phase = "a" | .build = 1')  # Add -c flag here
    
    update_config_line "$new_config"
    sync_version
    
    echo "Reset to alpha.1"
}

# Set build number directly
set_build() {
    local build="$1"
    
    # Validate build number
    if [[ ! "$build" =~ ^[0-9]+$ ]]; then
        echo "Error: Build must be a positive integer"
        exit 1
    fi
    
    # Update JSON config
    local current_config
    current_config=$(grep "VERSION_CONFIG:" "$VERSION_FILE" | sed 's/.*VERSION_CONFIG: //')

    local new_config
    new_config=$(echo "$current_config" | jq -c ".build = $build")
    
    update_config_line "$new_config"
    sync_version
    
    echo "Set build number to: $build"
}

# Track if we made changes to show final status
MADE_CHANGES=false

# Main command parsing
case "$1" in
    "build"|"b")
        bump_build
        MADE_CHANGES=true
        ;;
    "phase"|"p")
        if [[ -z "$2" ]]; then
            echo "Usage: $0 phase <a|b|rc|final>"
            exit 1
        fi
        set_phase "$2"
        MADE_CHANGES=true
        ;;
    "base")
        if [[ -z "$2" ]]; then
            echo "Usage: $0 base <x.y.z>"
            exit 1
        fi
        set_base "$2"
        MADE_CHANGES=true
        ;;
    "set-build")
        if [[ -z "$2" ]]; then
            echo "Usage: $0 set-build <number>"
            exit 1
        fi
        set_build "$2"
        MADE_CHANGES=true
        ;;
    "reset")
        reset_phase
        MADE_CHANGES=true
        ;;
    "show"|"status"|"")
        show_current
        ;;
    *)
        echo "Usage: $0 {build|phase|base|set-build|reset|show}"
        echo ""
        echo "Commands:"
        echo "  build, b              Bump build number"
        echo "  phase <phase>         Set development phase (a, b, rc, final)"
        echo "  base <version>        Set base version (x.y.z format)"
        echo "  set-build <number>    Set build number directly"
        echo "  reset                 Reset to alpha.1"
        echo "  show, status          Show current version info"
        echo ""
        echo "Examples:"
        echo "  $0 build              # 0.1.0a1 -> 0.1.0a2"
        echo "  $0 phase b            # 0.1.0a2 -> 0.1.0b2"
        echo "  $0 phase final        # 0.1.0b2 -> 0.1.0"
        echo "  $0 base 0.2.0         # Set new base version"
        echo "  $0 reset              # Reset to alpha.1"
        echo "  $0 set-build 1        # Reset build to 1"
        exit 1
        ;;
esac

# Only show final status if we made changes
if [[ "$MADE_CHANGES" == "true" ]]; then
    echo ""
    show_current
fi
