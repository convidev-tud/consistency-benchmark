#!/bin/bash


# Copyright (C) 2024 Karl Kegel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Prerequisites

# Check Python version
if ! python3 --version &> /dev/null; then
  echo "Python 3 is not installed. Please install Python 3."
  echo "If you have Python 3 installed, make sure its in PATH available as 'python3' command."
  exit 1
fi

# Check pip version
if ! pip3 --version &> /dev/null; then
  echo "pip3 is not installed. Please install pip3."
  echo "If you have pip3 installed, make sure its in PATH available as 'pip3' command."
  exit 1
fi

# Check Java is installed
if ! java -version &> /dev/null; then
  echo "Java is not installed. Please install Java."
  exit 1
fi

###

# Evolve every base model into its two variations and place them in gen/

cd ./tools
cd ./auto_evolv

# Check if .venv exists and create it if not
if [ ! -d ".venv" ]; then
  echo "Python virtual environment not found. Automatically create .venv!"
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Get every subdirectory of ./data
for dir in ../../data/*/; do
  if [ -d "$dir" ]; then
    folder_name=$(basename "$dir")
    realdir=$(realpath "$dir")
    echo "Data point: $folder_name"
    echo "Processing data directory: $realdir"
    echo "base model: $realdir/base.xml"
    echo "evolution a: $realdir/evolution_a.xml"
    echo "evolution b: $realdir/evolution_b.xml"
    echo move base.xml evolution_a.xml evolution_b.xml to gen/

    echo "Creating gen/${folder_name}..."
    mkdir -p ../../gen/"$folder_name"
    realdist=$(realpath ../../gen/"$folder_name")

    echo "Cleaning up gen/${folder_name}..."
    rm -f "$realdist"/*

    echo "Copying source files to gen/${folder_name}..."
    cp "$realdir"/base.xml "$realdist"/base.xml
    cp "$realdir"/evolution_a.xml "$realdist"/evolution_a.xml
    cp "$realdir"/evolution_b.xml "$realdist"/evolution_b.xml

    cp "../../meta/XSL/graph.xsd" "$realdist"/graph.xsd
    cp "../../meta/XSL/operations.xsd" "$realdist"/operations.xsd

    echo "Updating base.xml to use local graph.xsd..."
    sed -i '' 's|\.\./\.\./meta/XSL/graph.xsd|graph.xsd|g' "$realdist"/base.xml

    echo "Updating evolution.xml to use local operations.xsd..."
    sed -i '' 's|\.\./\.\./meta/XSL/operations.xsd|operations.xsd|g' "$realdist"/evolution_a.xml
    sed -i '' 's|\.\./\.\./meta/XSL/operations.xsd|operations.xsd|g' "$realdist"/evolution_b.xml

    echo "Generating evolutions for $folder_name..."

    echo "---"
    echo "Run evolve.py for evolution_a.xml..."
    output=$(python3 evolve.py "$realdir"/base.xml "$realdist"/graph.xsd "$realdist"/evolution_a.xml "$realdist"/operations.xsd "$realdist"/graph_a.xml ../../meta/XSL/graph_template.xml)
    echo "$output"

    echo "---"
    echo "Run evolve.py for evolution_b.xml..."
    output=$(python3 evolve.py "$realdir"/base.xml "$realdist"/graph.xsd "$realdist"/evolution_b.xml "$realdist"/operations.xsd "$realdist"/graph_b.xml ../../meta/XSL/graph_template.xml)
    echo "$output"

    echo "---"
    echo "Done."
  fi
done

# Deactivate the virtual environment
deactivate

echo "---"
echo "Generation of graph PlantUMl diagrams:"

cd .. 
cd ./graph_to_puml

# Check if .venv exists and create it if not
if [ ! -d ".venv" ]; then
  echo "Python virtual environment not found. Automatically create .venv!"
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Get every subdirectory of ./data
for gen in ../../gen/*/; do
  if [ -d "$gen" ]; then
    folder_name=$(basename "$gen")
    realdir=$(realpath "$gen")

    echo "Data point: $folder_name"
    echo "Processing generated graphs in directory: $realdir"
    echo "base model: $realdir/base.xml"
    echo "evolution a: $realdir/graph_a.xml"
    echo "evolution b: $realdir/graph_b.xml"

    echo "Generating PlantUML diagrams for $folder_name..."

    python convert.py "$realdir"/base.xml "$realdir"/graph.xsd "$realdir/"base.puml
    python convert.py "$realdir"/graph_a.xml "$realdir"/graph.xsd "$realdir/"graph_a.puml
    python convert.py "$realdir"/graph_b.xml "$realdir"/graph.xsd "$realdir/"graph_b.puml

    echo "Done."
    echo "Rendering PlantUML diagrams into PNGs for $folder_name..."

    java -jar ../libs/plantuml-lgpl-1.2024.8.jar -o "$realdir" "$realdir"/*.puml
  fi
done

echo "---"
echo "Done: Completed all tasks."