from roboto.domain import topics


TYPE_MAPPING_CANONICAL = {
    "bool": topics.CanonicalDataType.Number,
    "int8": topics.CanonicalDataType.Number,
    "uint8": topics.CanonicalDataType.Number,
    "int16": topics.CanonicalDataType.Number,
    "uint16": topics.CanonicalDataType.Number,
    "int32": topics.CanonicalDataType.Number,
    "uint32": topics.CanonicalDataType.Number,
    "int64": topics.CanonicalDataType.Number,
    "uint64": topics.CanonicalDataType.Number,
    "float32": topics.CanonicalDataType.Number,
    "float64": topics.CanonicalDataType.Number,
    "string": topics.CanonicalDataType.String,
    "time": topics.CanonicalDataType.Number,
    "duration": topics.CanonicalDataType.Number,
}


def parse_message_definition(definition):
    field_dict = {}
    for line in definition.split('\n'):
        stripped_line = line.strip()

        if stripped_line.startswith('#') or not stripped_line:
            continue

        #TODO: Look into byte fiels which is not a standard field type, but which appears in rosgraph_msgs/Log
        if stripped_line.startswith('byte') or not stripped_line:
            continue
        if "================================================================================" in stripped_line:
            break

        parts = stripped_line.split()
        if len(parts) >= 2:
            field_type = parts[0]
            field_name = parts[1]
            field_dict[field_name] = field_type
    return field_dict


def recursive_function(field_name, field_type, parsed_schemas, results):

    results.append((field_name, field_type))

    field_type_without_array = field_type.split('[')[0]

    if field_type_without_array in TYPE_MAPPING_CANONICAL.keys():

        if '[' in field_type:
            field_name_n = field_name + ".[*]"
            results.append((field_name_n, field_type_without_array))

        if field_type_without_array == "time":
            field_name_n = field_name + ".secs"
            results.append((field_name_n, "uint32"))
            field_name_n = field_name + ".nsecs"
            results.append((field_name_n, "uint32"))

        if field_type_without_array == "duration":
            field_name_n = field_name + ".secs"
            results.append((field_name_n, "int32"))
            field_name_n = field_name + ".nsecs"
            results.append((field_name_n, "int32"))

        return

    if field_type_without_array in parsed_schemas.keys():
        for key in parsed_schemas[field_type_without_array].keys():
            field_name_n = field_name + "." + key
            recursive_function(field_name_n, parsed_schemas[field_type_without_array][key], parsed_schemas, results)


def create_message_paths(input_text):

    field_dict = parse_message_definition(input_text)

    parsed_schemas, schema_name_lookup = parse_message_schemas(input_text)

    results = []
    for field_name, field_type in field_dict.items():
        recursive_function(field_name, field_type, parsed_schemas, results)

    for it, item in enumerate(results):
        field_type_without_array = item[1].split('[')[0]

        if field_type_without_array in schema_name_lookup.keys():
            results[it] = (item[0], schema_name_lookup[field_type_without_array])
        #     results[it][1] = field_type_without_array
        #
        print(results[it])
        #print(f"{field_name}, {field_type}")
    #
    #     field_type_without_array = field_type.split('[')[0]
    #
    #     if field_type_without_array not in TYPE_MAPPING_CANONICAL.keys():
    #         if field_type_without_array in parsed_schemas.keys():
    #
    #             for key in parsed_schemas[field_type_without_array].keys():
    #                 field_name_n = field_name + "." + key
    #                 print(f"{field_name_n}, {parsed_schemas[field_type_without_array][key]}")

    #
    #             print(f"Field type {field_type}, {parsed_schemas[field_type]}")
    #         return field_name, field_type, parsed_schemas
    #
    #     if field_type in parsed_schemas.keys():
    #         return field_name, field_type, parsed_schemas
    #
    #     else:
    #         return
    #
    # print(field_dict)
    #
    #
    # for field_name, field_type in field_dict.items():
    #     if field_type in TYPE_MAPPING_CANONICAL.keys():
    #         return field_name, field_type
    #
    #     if field_type in parsed_schemas.keys():
    #         return
    #
    #     else:
    #         return



        #     print(f"Field type {field_type}, {TYPE_MAPPING_CANONICAL[field_type]}")
        #
        #
        # if field_type not in TYPE_MAPPING_CANONICAL.keys():
        #     if field_type in parsed_schemas.keys():
        #         print(f"Field type {field_type}, {parsed_schemas[field_type]}")

            #     field_dict[key] = parsed_schemas[value]
            # else:
            #     field_dict[key] = value
            #


    # print(field_dict)


def parse_message_schemas(input_text):
    all_schemas = {}
    schema_name_lookup = {}
    sections = input_text.split("================================================================================")

    # Process each section to extract schema information
    for section in sections:
        # Split the section into lines for processing
        lines = section.strip().split("\n")
        if not lines:
            continue  # Skip empty sections

        # Identify and process nested schema definitions
        if lines[0].startswith("MSG:"):
            schema_name = lines[0].split("MSG:")[1].strip().split("/")[1]
            schema_name_lookup[schema_name] = lines[0].split("MSG:")[1].strip()

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

                fields[field_name] = field_type

            # Add the processed schema to the all_schemas dictionary
            all_schemas[schema_name] = fields

    return all_schemas, schema_name_lookup
