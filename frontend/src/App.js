import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';
import Spinner from 'react-bootstrap/Spinner';
import { useState } from 'react';
import axios from 'axios';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import BootstrapTable from 'react-bootstrap-table-next';

const Header = () => {
  return (
    <Navbar style={{ "marginBottom": "4vh" }}>
      <Navbar.Brand> <p className="h3"> Semantic query layer with Databricks Unity Catalog and OpenAI </p></Navbar.Brand>
    </Navbar>
  )
}

const Main = () => {
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState("");
  const [generatedQuery, setGeneratedQuery] = useState("");
  const [queryResults, setQueryResults] = useState({});
  const [naturalQueryLoading, setNaturalQueryLoading] = useState(false);
  const [sqlQueryLoading, setSqlQueryLoading] = useState(false);

  const CenteredSpinner = (props) => {
    return (
      <Spinner variant={props.variant} className='d-flex' style={{ margin: '0 auto', width: '10rem', height: '10rem' }} animation="border" />
    )
  }

  const onNaturalQuerySubmit = (e) => {
    setNaturalQueryLoading(true);
    setGeneratedQuery("");
    setQueryResults({});
    console.log(`Sending natural query to backend: ${naturalLanguageQuery}`);
    axios.post('http://localhost:8000/sql_query', { payload: naturalLanguageQuery })
      .then(res => {
        console.log(res);
        setGeneratedQuery(res.data.query);
        setNaturalQueryLoading(false);
      })
  };

  const onGeneratedQuerySubmit = (e) => {
    setSqlQueryLoading(true);
    console.log(`Sending generated query to backend: ${generatedQuery}`);
    axios.post('http://localhost:8000/execute_sql', { query: generatedQuery }, { validateStatus: false })
      .then(res => {
        console.log(res.data);
        setQueryResults(res.data);
        setSqlQueryLoading(false);
      })
  };

  const ResultView = () => {
    return (
      <div style={{ "marginTop": "4vh", "marginBottom": "10vh" }}>
        {
          sqlQueryLoading ? <CenteredSpinner variant="secondary" /> :
            <div>
              {
                ("data" in queryResults) && <div>
                  <p className="h4">Query results</p>
                  <BootstrapTable keyField={queryResults.columns[0].dataField} data={queryResults.data} columns={queryResults.columns} />
                </div>
              }
            </div>

        }
      </div>
    );
  }

  return (
    <div>
      <Form>
        <Form.Group>
          <Row>
            <Col>
              <Form.Control
                style={{ "minHeight": "10vh" }}
                as="textarea"
                placeholder="Enter your query in natural language"
                value={naturalLanguageQuery}
                onChange={(e) => setNaturalLanguageQuery(e.target.value)}
              />
            </Col>
            <Col xs lg="2">
              <Button
                variant="outline-primary"
                size="lg"
                style={{ "minWidth": "100%", "minHeight": "100%" }}
                onClick={onNaturalQuerySubmit}> Generate SQL
              </Button>
            </Col>
          </Row>
        </Form.Group>
      </Form>
      <Container style={{ "marginTop": "4vh" }}>
        {naturalQueryLoading ?
          <CenteredSpinner variant="primary" />
          :
          <Container>
            {
              generatedQuery &&
              <div>
                <p className="h4">Generated SQL Query</p>
                <SyntaxHighlighter language="sql" style={docco} >{generatedQuery}</SyntaxHighlighter>
                <Button
                  variant="outline-secondary"
                  size="lg"
                  style={{ "minWidth": "100%", "minHeight": "100%" }}
                  onClick={onGeneratedQuerySubmit}> Run this query
                </Button>
              </div>
            }
          </Container>
        }
        <Container>
          {
            ("detail" in queryResults) ?
              // true case - error in the results
              <Alert variant="danger">
                Error during executing the provided SQL query:
                <SyntaxHighlighter>
                  {queryResults.detail}
                </SyntaxHighlighter>
              </Alert> :
              // false case - results can be shown
              <ResultView />
          }
        </Container>
      </Container>
    </div>
  )
}

const App = () => {
  return (
    <Container>
      <Header />
      <Main />
    </Container>
  );
}

export default App;
