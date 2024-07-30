import pandas as pd
import networkx as nx
import folium

# Convert degrees, minutes, seconds to decimal degrees
def dms_to_dd(coord):
    if isinstance(coord, str):
        parts = coord.replace('°', '').replace("'", '').replace('"', '').split(' ')
        if len(parts) == 3:
            try:
                degrees, minutes, seconds = map(float, parts)
                dd = degrees + minutes / 60 + seconds / 3600
                if coord.endswith('S') or coord.endswith('W'):
                    dd *= -1
                return dd
            except ValueError:
                return coord
    return coord

# Get user input for disaster type
disaster_type = input("Enter the name of disaster as it is (Earthquake, Flood_Cyclone): ").lower()

if disaster_type == "earthquake":
    csv_file = "D:/CSE_SEM_05/disaster-mgmt-master/disaster-mgmt-master/build/dataset/Earthquake_India_2023 - Sheet1.csv"
elif disaster_type == "flood_cyclone":
    csv_file = "D:/CSE_SEM_05/disaster-mgmt-master/disaster-mgmt-master/build/dataset/Floods_Cyclones_India_2023 - Sheet1.csv"
else:
    print("Wrong disaster name found!")
    exit()

try:
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Print information about the loaded dataset
    print("Dataset Info:")
    print(df.info())

    # Print the first few rows of the dataset
    print("\nFirst few rows of the dataset:")
    print(df.head())

    # Get the required columns dynamically
    id_column = df.columns[0]
    longitude_column = df.columns[df.columns.str.lower().str.contains('long')][0]
    latitude_column = df.columns[df.columns.str.lower().str.contains('lat')][0]
    city_column = df.columns[df.columns.str.lower().str.contains('place|city')][0]

    # Clean up latitude and longitude columns
    df[latitude_column] = df[latitude_column].apply(dms_to_dd)
    df[longitude_column] = df[longitude_column].apply(dms_to_dd)

    # Convert latitude and longitude to numeric
    df[latitude_column] = pd.to_numeric(df[latitude_column], errors='coerce')
    df[longitude_column] = pd.to_numeric(df[longitude_column], errors='coerce')

    # Check if there is at least one valid row with numeric latitude and longitude
    valid_rows = df[(df[latitude_column].notnull()) & (df[longitude_column].notnull())]

    if not valid_rows.empty and all(column in valid_rows.columns for column in [id_column, latitude_column, longitude_column, city_column]):
        # Create a graph using networkx
        G = nx.Graph()

        # Add nodes to the graph with their coordinates
        for i, row in valid_rows.iterrows():
            G.add_node(row[id_column], pos=(row[longitude_column], row[latitude_column]))

        # Calculate distances between nodes and add edges to the graph
        for i in range(len(valid_rows)):
            for j in range(i + 1, len(valid_rows)):
                node1 = valid_rows.iloc[i][id_column]
                node2 = valid_rows.iloc[j][id_column]
                distance = ((valid_rows.iloc[i][longitude_column] - valid_rows.iloc[j][longitude_column])**2 +
                            (valid_rows.iloc[i][latitude_column] - valid_rows.iloc[j][latitude_column])**2)**0.5
                G.add_edge(node1, node2, weight=distance)

        # Apply Prim's algorithm to find the minimum spanning tree
        mst = nx.minimum_spanning_tree(G)

        # Print MST edges
        print(f"\nMinimum Spanning Tree Edges for {disaster_type.capitalize()}:")
        print(mst.edges())

        # Create a folium map centered at the average latitude and longitude
        avg_lat = valid_rows[latitude_column].mean()
        avg_lon = valid_rows[longitude_column].mean()
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

        # Plot nodes on the map
        for i, row in valid_rows.iterrows():
            folium.Marker([row[latitude_column], row[longitude_column]], popup=row[city_column]).add_to(m)

        # Plot all edges on the map
        for edge in G.edges():
            node1, node2 = edge
            lat1, lon1 = valid_rows[valid_rows[id_column] == node1][[latitude_column, longitude_column]].values[0]
            lat2, lon2 = valid_rows[valid_rows[id_column] == node2][[latitude_column, longitude_column]].values[0]
            if edge in mst.edges():
                folium.PolyLine([(lat1, lon1), (lat2, lon2)], color='red').add_to(m)
            else:
                folium.PolyLine([(lat1, lon1), (lat2, lon2)], color='blue').add_to(m)

        # Save the map to an HTML file
        m.save(f"map_{disaster_type}.html")

        print(f"Map for {disaster_type.capitalize()} created successfully. Check 'map_{disaster_type}.html'")

    else:
        print("No valid rows with required columns found.")

except FileNotFoundError:
    print(f"Error: File for {disaster_type.capitalize()} not found. Please enter a valid disaster type.")
except Exception as e:
    print(f"An error occurred: {e}. Please try again.")






















# import pandas as pd
# import networkx as nx
# import folium
# # Read the CSV file
# df = pd.read_csv("D:\CSE_SEM_05\disaster-mgmt-master\disaster-mgmt-master\public\dataset\Earthquake_India_2023 - Sheet1.csv")

# # Create a graph using networkx
# G = nx.Graph()

# # Add nodes to the graph with their coordinates
# for i, row in df.iterrows():
#     G.add_node(row['ID'], pos=(row['LONGITUDE'], row['LATITUDE']))

# # Calculate distances between nodes and add edges to the graph
# for i in range(len(df)):
#     for j in range(i + 1, len(df)):
#         node1 = df.iloc[i]['ID']
#         node2 = df.iloc[j]['ID']
#         distance = ((df.iloc[i]['LONGITUDE'] - df.iloc[j]['LONGITUDE'])**2 +
#                     (df.iloc[i]['LATITUDE'] - df.iloc[j]['LATITUDE'])**2)**0.5
#         G.add_edge(node1, node2, weight=distance)

# # Apply Prim's algorithm to find the minimum spanning tree
# mst = nx.minimum_spanning_tree(G)

# # Create a folium map centered at the average latitude and longitude
# avg_lat = df['LATITUDE'].mean()
# avg_lon = df['LONGITUDE'].mean()
# m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

# # Plot nodes on the map
# for i, row in df.iterrows():
#     folium.Marker([row['LATITUDE'], row['LONGITUDE']], popup=row['CITY']).add_to(m)

# # Plot all edges on the map
# for edge in G.edges():
#     node1, node2 = edge
#     lat1, lon1 = df[df['ID'] == node1][['LATITUDE', 'LONGITUDE']].values[0]
#     lat2, lon2 = df[df['ID'] == node2][['LATITUDE', 'LONGITUDE']].values[0]
#     if edge in mst.edges():
#         folium.PolyLine([(lat1, lon1), (lat2, lon2)], color='red').add_to(m)
#     else:
#         folium.PolyLine([(lat1, lon1), (lat2, lon2)], color='blue').add_to(m)

# # Save the map to an HTML file
# m.save("map.html")
