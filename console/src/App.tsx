
import useCurrentUser from './hooks/useCurrentUser';
import { RouterProvider, createBrowserRouter } from 'react-router';
import { privateRoutes } from './routes/privateRoutes';


// function App() {
//   return (
//     <Router>
//       <Layout style={{ minHeight: '100vh' }}>
//         <Navigation />
//         <Routes>
//           <Route path="/" element={<Navigate to="/jobs" replace />} />
//           <Route path="/jobs" element={<Jobs />} />
//           <Route path="/templates" element={<Templates />} />
//           <Route path="/tools/parser" element={<LogParserPage />} />
//           <Route
//             path="*"
//             element={
//               <Content style={{ padding: '50px', textAlign: 'center' }}>
//                 <Result
//                   status="404"
//                   title="404"
//                   subTitle="Sorry, the page you visited does not exist."
//                   extra={
//                     <Button type="primary" onClick={() => window.location.href = '/jobs'}>
//                       Back to Jobs
//                     </Button>
//                   }
//                 />
//               </Content>
//             }
//           />
//         </Routes>
//       </Layout>
//     </Router>
//   );
// }

const App = () => {
  const currentUser = useCurrentUser();

  return (
    <div data-testid="app-container">
      <RouterProvider router={createBrowserRouter([privateRoutes(currentUser.data?.role.name)])} />
    </div>
  );
};

export default App;
