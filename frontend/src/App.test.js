import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the owner login screen', async () => {
  render(<App />);
  expect(await screen.findByText(/owner access/i)).toBeInTheDocument();
  expect(screen.getByText(/open the live security console/i)).toBeInTheDocument();
});
