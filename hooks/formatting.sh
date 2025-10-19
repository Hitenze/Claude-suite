#!/bin/bash
# Professional formatting hook for CLAUDE code
# Applies consistent formatting based on file extension

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track formatting status
formatted_count=0
error_count=0

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Process each file
for file in $CLAUDE_FILE_PATHS; do
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}Skipping non-existent file: $file${NC}"
        continue
    fi
    
    echo -n "Formatting $file... "
    
    case "$file" in
        *.cpp|*.cc|*.c|*.h|*.hpp|*.cxx)
            # C/C++ files - use clang-format with custom style
            if command_exists clang-format; then
                # Look for .clang-format in project root or use inline style
                if [ -f .clang-format ]; then
                    clang-format -i "$file" 2>/dev/null
                else
                    # Inline style with 3 spaces indentation
                    clang-format -i --style="{BasedOnStyle: Google, IndentWidth: 3, UseTab: Never, ColumnLimit: 100}" "$file" 2>/dev/null
                fi
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] C/C++${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] C/C++ formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] clang-format not found${NC}"
            fi
            ;;
            
        *.py)
            # Python files - use black
            if command_exists black; then
                black --quiet --line-length 88 "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] Python${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] Python formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] black not found${NC}"
            fi
            ;;
            
        *.js|*.jsx|*.ts|*.tsx)
            # JavaScript/TypeScript - use prettier if available
            if command_exists prettier; then
                prettier --write --loglevel silent "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] JS/TS${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] JS/TS formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] prettier not found${NC}"
            fi
            ;;
            
        *.json)
            # JSON files - use jq if available
            if command_exists jq; then
                jq . "$file" > "$file.tmp" 2>/dev/null && mv "$file.tmp" "$file"
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] JSON${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] JSON formatting failed${NC}"
                    ((error_count++))
                fi
            elif command_exists prettier; then
                prettier --write --loglevel silent "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] JSON${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] JSON formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] jq/prettier not found${NC}"
            fi
            ;;
            
        *.md)
            # Markdown files - use prettier or markdownlint
            if command_exists prettier; then
                prettier --write --prose-wrap always --loglevel silent "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] Markdown${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] Markdown formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] prettier not found${NC}"
            fi
            ;;
            
        *.yaml|*.yml)
            # YAML files - use prettier or yamlfmt
            if command_exists prettier; then
                prettier --write --loglevel silent "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] YAML${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] YAML formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] prettier not found${NC}"
            fi
            ;;
            
        *.sh|*.bash)
            # Shell scripts - use shfmt if available
            if command_exists shfmt; then
                shfmt -i 2 -ci -w "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] Shell${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] Shell formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] shfmt not found${NC}"
            fi
            ;;
            
        *.go)
            # Go files - use gofmt
            if command_exists gofmt; then
                gofmt -w "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] Go${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] Go formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] gofmt not found${NC}"
            fi
            ;;
            
        *.rs)
            # Rust files - use rustfmt
            if command_exists rustfmt; then
                rustfmt --edition 2021 "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] Rust${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] Rust formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] rustfmt not found${NC}"
            fi
            ;;
            
        *.xml)
            # XML files - use xmllint
            if command_exists xmllint; then
                xmllint --format "$file" --output "$file" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}[OK] XML${NC}"
                    ((formatted_count++))
                else
                    echo -e "${RED}[ERROR] XML formatting failed${NC}"
                    ((error_count++))
                fi
            else
                echo -e "${YELLOW}[WARNING] xmllint not found${NC}"
            fi
            ;;
            
        *)
            echo -e "${YELLOW}[WARNING] No formatter configured${NC}"
            ;;
    esac
done

# Summary
echo ""
echo -e "${GREEN}Formatting complete:${NC} $formatted_count files formatted successfully"
if [ $error_count -gt 0 ]; then
    echo -e "${RED}Errors:${NC} $error_count files failed to format"
fi