"""
Templates Module
Provides templates for Spring Boot code generation
"""

def get_entity_template():
    """
    Template for JPA entity class
    """
    return """package {{package}};

{{imports}}

/**
 * {{entity_description}}
 */
@Entity
@Table(name = "{{table_name}}")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class {{entity_name}} {
{{fields}}
}
"""

def get_repository_template():
    """
    Template for Spring Data JPA repository
    """
    return """package {{package}};

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
{{entity_import}}

/**
 * Repository interface for {{entity_name}} entity
 */
@Repository
public interface {{entity_name}}Repository extends JpaRepository<{{entity_name}}, Long> {
    // You can add custom query methods here
}
"""

def get_service_template():
    """
    Template for service class
    """
    return """package {{package}};

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
{{entity_import}}

/**
 * Service class for {{entity_name}} entity
 */
@Service
@Transactional
public class {{entity_name}}Service {

    private final {{entity_name}}Repository {{entity_var}}Repository;

    @Autowired
    public {{entity_name}}Service({{entity_name}}Repository {{entity_var}}Repository) {
        this.{{entity_var}}Repository = {{entity_var}}Repository;
    }

    /**
     * Get all {{entity_name}} entities
     * 
     * @return List of {{entity_name}}DTO
     */
    public List<{{entity_name}}DTO> findAll() {
        return {{entity_var}}Repository.findAll().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    /**
     * Get {{entity_name}} by ID
     * 
     * @param id {{entity_name}} ID
     * @return {{entity_name}}DTO
     */
    public Optional<{{entity_name}}DTO> findById(Long id) {
        return {{entity_var}}Repository.findById(id)
                .map(this::convertToDTO);
    }

    /**
     * Create a new {{entity_name}}
     * 
     * @param {{entity_var}}DTO {{entity_name}}DTO
     * @return Created {{entity_name}}DTO
     */
    public {{entity_name}}DTO create({{entity_name}}DTO {{entity_var}}DTO) {
        {{entity_name}} {{entity_var}} = convertToEntity({{entity_var}}DTO);
        {{entity_name}} saved{{entity_name}} = {{entity_var}}Repository.save({{entity_var}});
        return convertToDTO(saved{{entity_name}});
    }

    /**
     * Update an existing {{entity_name}}
     * 
     * @param id {{entity_name}} ID
     * @param {{entity_var}}DTO {{entity_name}}DTO
     * @return Updated {{entity_name}}DTO
     */
    public Optional<{{entity_name}}DTO> update(Long id, {{entity_name}}DTO {{entity_var}}DTO) {
        if (!{{entity_var}}Repository.existsById(id)) {
            return Optional.empty();
        }
        
        {{entity_var}}DTO.setId(id);
        {{entity_name}} {{entity_var}} = convertToEntity({{entity_var}}DTO);
        {{entity_name}} updated{{entity_name}} = {{entity_var}}Repository.save({{entity_var}});
        return Optional.of(convertToDTO(updated{{entity_name}}));
    }

    /**
     * Delete {{entity_name}} by ID
     * 
     * @param id {{entity_name}} ID
     * @return true if deleted, false if not found
     */
    public boolean deleteById(Long id) {
        if (!{{entity_var}}Repository.existsById(id)) {
            return false;
        }
        
        {{entity_var}}Repository.deleteById(id);
        return true;
    }

    /**
     * Convert {{entity_name}} entity to DTO
     * 
     * @param {{entity_var}} {{entity_name}} entity
     * @return {{entity_name}}DTO
     */
    private {{entity_name}}DTO convertToDTO({{entity_name}} {{entity_var}}) {
        {{entity_name}}DTO dto = new {{entity_name}}DTO();
        dto.setId({{entity_var}}.getId());
        // Set other fields here based on the entity
        // This will be customized based on actual entity fields
        return dto;
    }

    /**
     * Convert {{entity_name}}DTO to entity
     * 
     * @param dto {{entity_name}}DTO
     * @return {{entity_name}} entity
     */
    private {{entity_name}} convertToEntity({{entity_name}}DTO dto) {
        {{entity_name}} {{entity_var}} = new {{entity_name}}();
        if (dto.getId() != null) {
            {{entity_var}}.setId(dto.getId());
        }
        // Set other fields here based on the DTO
        // This will be customized based on actual DTO fields
        return {{entity_var}};
    }
}
"""

def get_controller_template():
    """
    Template for REST controller
    """
    return """package {{package}};

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import javax.validation.Valid;
import java.util.List;
{{entity_import}}
{{swagger_imports}}

/**
 * REST controller for managing {{entity_name}} entities
 */
@RestController
@RequestMapping("/api/{{endpoint}}")
{{swagger_api_annotations}}
public class {{entity_name}}Controller {

    private final {{entity_name}}Service {{entity_var}}Service;

    @Autowired
    public {{entity_name}}Controller({{entity_name}}Service {{entity_var}}Service) {
        this.{{entity_var}}Service = {{entity_var}}Service;
    }

{{swagger_method_annotations}}
    @GetMapping
    public ResponseEntity<List<{{entity_name}}DTO>> getAll{{entity_name}}s() {
        List<{{entity_name}}DTO> {{entity_var}}s = {{entity_var}}Service.findAll();
        return ResponseEntity.ok({{entity_var}}s);
    }

    @GetMapping("/{id}")
    public ResponseEntity<{{entity_name}}DTO> get{{entity_name}}(@PathVariable Long id) {
        return {{entity_var}}Service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<{{entity_name}}DTO> create{{entity_name}}(@Valid @RequestBody {{entity_name}}DTO {{entity_var}}DTO) {
        {{entity_name}}DTO created{{entity_name}} = {{entity_var}}Service.create({{entity_var}}DTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(created{{entity_name}});
    }

    @PutMapping("/{id}")
    public ResponseEntity<{{entity_name}}DTO> update{{entity_name}}(
            @PathVariable Long id,
            @Valid @RequestBody {{entity_name}}DTO {{entity_var}}DTO) {
        return {{entity_var}}Service.update(id, {{entity_var}}DTO)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete{{entity_name}}(@PathVariable Long id) {
        if ({{entity_var}}Service.deleteById(id)) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
"""

def get_exception_handler_template():
    """
    Template for exception handler class
    """
    return """package {{package}}.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Object> handleValidationExceptions(
            MethodArgumentNotValidException ex, WebRequest request) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });
        
        ErrorResponse errorResponse = new ErrorResponse(
                LocalDateTime.now(),
                HttpStatus.BAD_REQUEST.value(),
                "Validation Error",
                errors.toString(),
                request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGlobalException(
            Exception ex, WebRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                LocalDateTime.now(),
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                "Internal Server Error",
                ex.getMessage(),
                request.getDescription(false)
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}

class ErrorResponse {
    private LocalDateTime timestamp;
    private int status;
    private String error;
    private String message;
    private String path;

    public ErrorResponse(LocalDateTime timestamp, int status, String error, String message, String path) {
        this.timestamp = timestamp;
        this.status = status;
        this.error = error;
        this.message = message;
        this.path = path;
    }

    // Getters and setters
    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }
}
"""

def get_template_code(template_name):
    """
    Get template code by template name
    
    Args:
        template_name (str): Name of the template
        
    Returns:
        str: Template code or None if not found
    """
    templates = {
        'entity': get_entity_template(),
        'repository': get_repository_template(),
        'service': get_service_template(),
        'controller': get_controller_template(),
        'exception_handler': get_exception_handler_template(),
        
        # Sample entity templates
        'sample_product': """@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "name", nullable = false)
    private String name;
    
    @Column(name = "description")
    private String description;
    
    @Column(name = "price", nullable = false)
    private BigDecimal price;
    
    @Column(name = "sku", unique = true)
    private String sku;
    
    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;
    
    // Getters and setters
}""",
        
        'sample_user': """@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "username", nullable = false, unique = true)
    private String username;
    
    @Column(name = "email", nullable = false, unique = true)
    private String email;
    
    @Column(name = "password", nullable = false)
    private String password;
    
    @Column(name = "first_name")
    private String firstName;
    
    @Column(name = "last_name")
    private String lastName;
    
    @Column(name = "active")
    private Boolean active = true;
    
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<Order> orders;
    
    // Getters and setters
}""",
        
        'sample_order': """@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "order_number", nullable = false, unique = true)
    private String orderNumber;
    
    @Column(name = "order_date", nullable = false)
    private LocalDateTime orderDate;
    
    @Column(name = "status")
    private String status;
    
    @Column(name = "total_amount", nullable = false)
    private BigDecimal totalAmount;
    
    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderItem> items;
    
    // Getters and setters
}"""
    }
    
    return templates.get(template_name)
