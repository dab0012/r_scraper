
-- Create the package table
CREATE TABLE packages (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(255) NOT NULL,
    publication_date DATE NOT NULL,
    requires_compilation BOOLEAN NOT NULL,
    in_cran BOOLEAN,
    in_bioconductor BOOLEAN,
    mantainer VARCHAR(255) NOT NULL,
    author_data TEXT,
    license VARCHAR(255) NOT NULL
);

-- Tables to store dependencies
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL
);

-- Table to store the dependencies of the packages
CREATE TABLE package_dependency (
    package_id INTEGER NOT NULL,
    dependency_id INTEGER NOT NULL,
    PRIMARY KEY (package_id, dependency_id),
    FOREIGN KEY (package_id) REFERENCES packages(id),
    FOREIGN KEY (dependency_id) REFERENCES dependencies(id)
);

-- Tables to store the url of the packages
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    url VARCHAR(255) NOT NULL,
    package_id INTEGER NOT NULL,
    FOREIGN KEY (package_id) REFERENCES packages(id)
);

-- Table to store the links of the packages
CREATE TABLE package_link (
    package_id INTEGER NOT NULL,
    url_id INTEGER NOT NULL,
    PRIMARY KEY (package_id, url_id),
    FOREIGN KEY (package_id) REFERENCES packages(id),
    FOREIGN KEY (url_id) REFERENCES links(id)
);