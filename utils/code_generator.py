"""
Code Generator Module
Generates Spring Boot code from entity definitions
"""

import logging
from utils.templates import get_entity_template, get_controller_template, get_service_template, get_repository_template

logger = logging.getLogger(__name__)

def generate_spring_boot_code(entity_data):
    """
    Generate Spring Boot code from entity definitions
    
    Args:
        entity_data (dict): Dictionary of entity definitions
        
    Returns:
        dict: Dictionary of generated code files
    """
    try:
        logging.debug(f"generate_spring_boot_code called with entity_data: {entity_data}")
        generated_files = {}
        
        # Generate a package name (default)
        package_name = "com.example.demo"
        
        # Generate code for each entity
        for entity_name, entity_info in entity_data.items():
            # Generate entity/model class
            entity_code = generate_entity_class(package_name, entity_name, entity_info)
            generated_files[f"src/main/java/{package_name.replace('.', '/')}/model/{entity_name}.java"] = entity_code
            
            # Generate repository interface
            if entity_info.get('config', {}).get('generateRepository', True):
                repo_code = generate_repository_interface(package_name, entity_name, entity_info)
                generated_files[f"src/main/java/{package_name.replace('.', '/')}/repository/{entity_name}Repository.java"] = repo_code
            
            # Generate service class
            if entity_info.get('config', {}).get('generateService', True):
                service_code = generate_service_class(package_name, entity_name, entity_info)
                generated_files[f"src/main/java/{package_name.replace('.', '/')}/service/{entity_name}Service.java"] = service_code
            
            # Generate controller class
            if entity_info.get('config', {}).get('generateController', True):
                controller_code = generate_controller_class(package_name, entity_name, entity_info)
                generated_files[f"src/main/java/{package_name.replace('.', '/')}/controller/{entity_name}Controller.java"] = controller_code
            
            # Generate DTO classes if needed
            dto_code = generate_dto_class(package_name, entity_name, entity_info)
            generated_files[f"src/main/java/{package_name.replace('.', '/')}/dto/{entity_name}DTO.java"] = dto_code
        
        # Generate application.properties
        props_code = generate_application_properties()
        generated_files["src/main/resources/application.properties"] = props_code
        
        # Generate pom.xml (or build.gradle)
        pom_code = generate_pom_xml(entity_data)
        generated_files["pom.xml"] = pom_code
        
        # Generate main application class
        app_code = generate_main_application_class(package_name, entity_data)
        generated_files[f"src/main/java/{package_name.replace('.', '/')}/Application.java"] = app_code
        
        # Generate README.md
        readme_code = generate_readme(entity_data)
        generated_files["README.md"] = readme_code
        
        return generated_files
    except Exception as e:
        logger.error(f"Error generating Spring Boot code: {str(e)}")
        raise

def generate_entity_class(package_name, entity_name, entity_info):
    """Generate JPA entity class"""
    fields = entity_info.get('fields', [])
    imports = set([
        "import javax.persistence.*;",
        "import lombok.Data;",
        "import lombok.NoArgsConstructor;",
        "import lombok.AllArgsConstructor;"
    ])
    
    field_declarations = []
    
    # Add ID field by default
    field_declarations.append("""    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
""")
    
    # Process fields
    for field in fields:
        field_name = field.get('name')
        field_type = field.get('type')
        validations = field.get('validations', [])
        
        # Add imports based on field type
        if field_type == 'Date':
            imports.add("import java.util.Date;")
        elif field_type == 'LocalDate':
            imports.add("import java.time.LocalDate;")
        elif field_type == 'LocalDateTime':
            imports.add("import java.time.LocalDateTime;")
        elif field_type == 'BigDecimal':
            imports.add("import java.math.BigDecimal;")
        elif field_type == 'Entity':
            referenced_entity = field.get('reference', 'Object')
            imports.add(f"import {package_name}.model.{referenced_entity};")
        elif field_type == 'Collection':
            referenced_entity = field.get('reference', 'Object')
            imports.add(f"import {package_name}.model.{referenced_entity};")
            imports.add("import java.util.List;")
            imports.add("import java.util.ArrayList;")
            field_type = f"List<{referenced_entity}>"
        
        # Add validation imports
        if 'required' in validations:
            imports.add("import javax.validation.constraints.NotNull;")
        if 'unique' in validations:
            # Nothing to import for unique, it's a JPA annotation
            pass
        
        # Build field declaration
        field_code = []
        
        # Add column annotation
        column_attrs = []
        if 'required' in validations:
            column_attrs.append("nullable = false")
        if 'unique' in validations:
            column_attrs.append("unique = true")
        
        if column_attrs:
            field_code.append(f"    @Column({', '.join(column_attrs)})")
        else:
            field_code.append("    @Column")
        
        # Add validation annotations
        if 'required' in validations:
            field_code.append("    @NotNull")
        
        # Add relationship annotations for entity references
        if field_type == 'Entity':
            referenced_entity = field.get('reference', 'Object')
            field_code.append("    @ManyToOne")
            field_code.append(f"    @JoinColumn(name = \"{field_name.lower()}_id\")")
            field_type = referenced_entity
        elif field_type.startswith('List<'):
            referenced_entity = field.get('reference', 'Object')
            field_code.append("    @OneToMany(mappedBy = \"" + entity_name.lower() + "\", cascade = CascadeType.ALL)")
        
        # Add field declaration
        field_code.append(f"    private {field_type} {field_name};")
        
        field_declarations.append('\n'.join(field_code) + '\n')
    
    # Import sorting and formatting
    sorted_imports = sorted(list(imports))
    imports_str = '\n'.join(sorted_imports)
    
    # Apply entity template
    template = get_entity_template()
    
    generated_code = template.replace(
        '{{package}}', package_name + '.model'
    ).replace(
        '{{imports}}', imports_str
    ).replace(
        '{{entity_name}}', entity_name
    ).replace(
        '{{table_name}}', entity_name.lower() + 's'
    ).replace(
        '{{entity_description}}', entity_info.get('description', f"Represents a {entity_name} entity")
    ).replace(
        '{{fields}}', '\n'.join(field_declarations)
    )
    
    return generated_code

def generate_repository_interface(package_name, entity_name, entity_info):
    """Generate Spring Data JPA repository interface"""
    template = get_repository_template()
    
    generated_code = template.replace(
        '{{package}}', package_name + '.repository'
    ).replace(
        '{{entity_import}}', f"import {package_name}.model.{entity_name};"
    ).replace(
        '{{entity_name}}', entity_name
    )
    
    return generated_code

def generate_service_class(package_name, entity_name, entity_info):
    """Generate service class with business logic"""
    template = get_service_template()
    
    generated_code = template.replace(
        '{{package}}', package_name + '.service'
    ).replace(
        '{{entity_import}}', f"import {package_name}.model.{entity_name};\nimport {package_name}.repository.{entity_name}Repository;\nimport {package_name}.dto.{entity_name}DTO;"
    ).replace(
        '{{entity_name}}', entity_name
    ).replace(
        '{{entity_var}}', entity_name.lower()
    )
    
    return generated_code

def generate_controller_class(package_name, entity_name, entity_info):
    """Generate REST controller class"""
    template = get_controller_template()
    endpoint = entity_name.lower() + 's'
    
    # Add Swagger annotations if requested
    swagger_imports = ""
    swagger_api_annotations = ""
    swagger_method_annotations = ""
    
    if entity_info.get('config', {}).get('generateSwagger', True):
        swagger_imports = """import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;"""
        
        swagger_api_annotations = f"""@Tag(name = "{entity_name} Management", description = "Operations related to {entity_name}")"""
        
        swagger_method_annotations = """    @Operation(summary = "Get all %s", description = "Returns a list of all %s")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Successfully retrieved list"),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })""" % (endpoint, endpoint)
    
    generated_code = template.replace(
        '{{package}}', package_name + '.controller'
    ).replace(
        '{{entity_import}}', f"import {package_name}.model.{entity_name};\nimport {package_name}.service.{entity_name}Service;\nimport {package_name}.dto.{entity_name}DTO;"
    ).replace(
        '{{swagger_imports}}', swagger_imports
    ).replace(
        '{{swagger_api_annotations}}', swagger_api_annotations
    ).replace(
        '{{swagger_method_annotations}}', swagger_method_annotations
    ).replace(
        '{{entity_name}}', entity_name
    ).replace(
        '{{entity_var}}', entity_name.lower()
    ).replace(
        '{{endpoint}}', endpoint
    )
    
    return generated_code

def generate_dto_class(package_name, entity_name, entity_info):
    """Generate DTO (Data Transfer Object) class"""
    fields = entity_info.get('fields', [])
    imports = set([
        "import lombok.Data;",
        "import lombok.NoArgsConstructor;",
        "import lombok.AllArgsConstructor;"
    ])
    
    field_declarations = []
    
    # Add ID field
    field_declarations.append("    private Long id;")
    
    # Process fields
    for field in fields:
        field_name = field.get('name')
        field_type = field.get('type')
        
        # Add imports based on field type
        if field_type == 'Date':
            imports.add("import java.util.Date;")
        elif field_type == 'LocalDate':
            imports.add("import java.time.LocalDate;")
        elif field_type == 'LocalDateTime':
            imports.add("import java.time.LocalDateTime;")
        elif field_type == 'BigDecimal':
            imports.add("import java.math.BigDecimal;")
        elif field_type == 'Entity':
            # For DTO, we'll just use the ID of the referenced entity
            field_type = "Long"
        elif field_type == 'Collection':
            imports.add("import java.util.List;")
            field_type = "List<Long>"
        
        # Add field declaration
        field_declarations.append(f"    private {field_type} {field_name};")
    
    # Import sorting and formatting
    sorted_imports = sorted(list(imports))
    imports_str = '\n'.join(sorted_imports)
    
    # Create DTO class
    dto_code = f"""package {package_name}.dto;

{imports_str}

/**
 * DTO for {entity_name}
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class {entity_name}DTO {{
{chr(10).join(field_declarations)}
}}
"""
    
    return dto_code

def generate_application_properties():
    """Generate application.properties file"""
    props = """# Spring DataSource Configuration
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=password
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect

# Hibernate Configuration
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# H2 Console Configuration
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console

# Server Configuration
server.port=8080

# Logging Configuration
logging.level.org.springframework=INFO
logging.level.com.example=DEBUG

# Swagger Configuration
springdoc.api-docs.path=/api-docs
springdoc.swagger-ui.path=/swagger-ui.html
springdoc.swagger-ui.operationsSorter=method
"""
    return props

def generate_pom_xml(entity_data):
    """Generate Maven pom.xml file"""
    # Determine if Swagger is needed
    need_swagger = any(entity_info.get('config', {}).get('generateSwagger', True) 
                      for entity_info in entity_data.values())
    
    swagger_dependency = ""
    if need_swagger:
        swagger_dependency = """
        <!-- OpenAPI/Swagger -->
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-ui</artifactId>
            <version>1.6.9</version>
        </dependency>"""
    
    pom_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.5</version>
        <relativePath/>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo Spring Boot REST API</description>
    
    <properties>
        <java.version>11</java.version>
    </properties>
    
    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        
        <!-- H2 Database -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        %s
        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
""" % swagger_dependency
    
    return pom_xml

def generate_main_application_class(package_name, entity_data):
    """Generate main Spring Boot application class"""
    app_code = f"""package {package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;

/**
 * Main Spring Boot Application class
 */
@SpringBootApplication
@OpenAPIDefinition(
    info = @Info(
        title = "Spring Boot REST API",
        version = "1.0.0",
        description = "API Documentation for Spring Boot REST API"
    )
)
public class Application {{
    public static void main(String[] args) {{
        SpringApplication.run(Application.class, args);
    }}
}}
"""
    return app_code

def generate_readme(entity_data):
    """Generate README.md file with instructions"""
    entity_names = list(entity_data.keys())
    entity_list = "\n".join([f"- {name}" for name in entity_names])
    
    readme = f"""# Spring Boot REST API

A RESTful API built with Spring Boot for managing {', '.join(entity_names)}.

## Entities

{entity_list}

## Getting Started

### Prerequisites

- Java 11 or higher
- Maven

### Running the Application

1. Clone the repository
2. Navigate to the project directory
3. Run `mvn spring-boot:run`
4. The application will start on http://localhost:8080

## API Documentation

The API documentation is available at http://localhost:8080/swagger-ui.html when the application is running.

## API Endpoints

For each entity, the following endpoints are available:

- `GET /api/{{endpoint}}` - Get all entities
- `GET /api/{{endpoint}}/{{id}}` - Get a specific entity by ID
- `POST /api/{{endpoint}}` - Create a new entity
- `PUT /api/{{endpoint}}/{{id}}` - Update an existing entity
- `DELETE /api/{{endpoint}}/{{id}}` - Delete an entity

Replace `{{endpoint}}` with the plural form of the entity name in lowercase, e.g., `products`, `customers`, etc.

## Database

The application uses an H2 in-memory database by default. You can access the H2 console at http://localhost:8080/h2-console with the following credentials:

- JDBC URL: `jdbc:h2:mem:testdb`
- Username: `sa`
- Password: `password`

To use a different database, update the `application.properties` file with the appropriate database configuration.

## Built With

- Spring Boot
- Spring Data JPA
- H2 Database
- Lombok
- SpringDoc OpenAPI (Swagger)

## License

This project is licensed under the MIT License.
"""
    
    return readme
