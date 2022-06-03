import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

const App = () => {
  return (
    <Container>
      <Navbar style={{ "marginBottom": "4vh" }}>
        <Navbar.Brand> <p className="h3"> Semantic query layer with Databricks Unity Catalog and OpenAI </p></Navbar.Brand>
      </Navbar>
      <Row>
        <Col>
          <Form>
            <Form.Group>
              <Form.Label class="h4"> Query in natural language</Form.Label>
              <Form.Control style={{ "minHeight": "10vh" }} as="textarea" placeholder="Enter your query in natural language" />
            </Form.Group>
          </Form>
        </Col>
        <Col xs lg="2">
          <Button variant="outline-primary" size="lg" style={{ "minWidth": "100%", "minHeight": "100%" }}> Run Query! </Button>
        </Col>
      </Row>
      <Container style={{ "marginTop": "4vh" }}>
        <Row>
          <Col> 
            <p className="h4">Generated SQL Query</p> 
          </Col>
          <Col>
            <p className="h4">Query results</p> 
          </Col>
        </Row>
      </Container>
    </Container>
  );
}

export default App;
