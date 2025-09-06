def get_if_else_statement_fmt(length: int, always_comb: bool = True, implicit_final_condition: bool = True, case_format: bool = False, unique: bool = False) -> str:
    """
    Generates a formatted string for an if-else or case statement in SystemVerilog.
    Args:
        length (int): The number of conditions to generate.
        always_comb (bool, optional): If True, wraps the statement in an always_comb block. Defaults to True.
        implicit_final_condition (bool, optional): If True, the final else condition is implicit. Defaults to True.
        case_format (bool, optional): If True, generates a case statement instead of if-else. Defaults to False.
    Returns:
        str: A formatted string representing the if-else or case statement.
    """
    
    if always_comb:
        out_fmt = "{indent}always_comb begin\n"
    else:
        out_fmt = ""
        
    if case_format is True:
        
        if unique:
            out_fmt += "{indent}unique case ({val})\n"
        else:
            out_fmt += "{indent}case ({val})\n"
        for i in range(length+1):
            out_fmt += f"{{indent}}\t{{condition{i}}} : {{assign{i}}}"
            
        out_fmt += "{indent}endcase\n"
    else:
        for i in range(length):
            if i == 0:
                out_fmt += f"{{indent}}\tif ({{condition{i}}}) begin\n"
            elif i == length-1 and implicit_final_condition is True:
                out_fmt += "{indent}\tend else begin\n"
            else:
                out_fmt += f"{{indent}}\tend else if ({{condition{i}}}) begin\n"
                
            # out_fmt += f"{{indent}}\t\t{{lhs}} = {{rhs{i}}};\n"
            out_fmt += f"{{assign{i}}}"

        out_fmt += "{indent}\tend\n"
    
    if always_comb:
        out_fmt += "{indent}end\n"
    
    return out_fmt