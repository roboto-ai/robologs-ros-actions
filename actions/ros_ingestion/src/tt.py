def parse_message_schemas(input_text):
    # Initialize a dictionary to hold all schema definitions
    all_schemas = {}
    
    # Split the input text into sections based on the separator line
    sections = input_text.split("================================================================================")
    
    # Process each section to extract schema information
    for section in sections:
        # Split the section into lines for processing
        lines = section.strip().split("\n")
        if not lines:
            continue  # Skip empty sections
        
        # Identify and process nested schema definitions
        if lines[0].startswith("MSG:"):
            schema_name = lines[0].split("MSG:")[1].strip()
            fields = {}
            
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue  # Skip comments and empty lines
                
                # Split line into components (type and name)
                parts = line.split()
                if len(parts) < 2:
                    continue  # Skip invalid lines
                
                field_type = parts[0]
                field_name = parts[1]
                
                # For arrays, append '[]' to type
                if field_name.endswith("[]"):
                    field_name = field_name.replace("[]", "")
                    field_type += "[]"
                
                # Handle special cases, like merging "time stamp" into one field
                if field_type == "time" and field_name.startswith("stamp."):
                    field_name = "stamp"
                
                fields[field_name] = field_type
            
            # Add the processed schema to the all_schemas dictionary
            all_schemas[schema_name] = fields
    
    return all_schemas

# Use the provided example input text or replace it with your own
input_text = """
================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

================================================================================
MSG: sensor_msgs/PointField
# This message holds the description of one point entry in the
# PointCloud2 message format.
uint8 INT8    = 1
uint8 UINT8   = 2
uint8 INT16   = 3
uint8 UINT16  = 4
uint8 INT32   = 5
uint8 UINT32  = 6
uint8 FLOAT32 = 7
uint8 FLOAT64 = 8

string name      # Name of field
uint32 offset    # Offset from start of point struct
uint8  datatype  # Datatype enumeration, see above
uint32 count     # How many elements in the field
"""

# Parse the input text and output the dictionary of schemas
parsed_schemas = parse_message_schemas(input_text)
for schema_name, fields in parsed_schemas.items():
    print(f"{schema_name}: {fields}\n")
