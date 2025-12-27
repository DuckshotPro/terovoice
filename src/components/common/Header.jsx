import React from 'react';
import { NavLink } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-white shadow">
      <div className="container mx-auto py-4 px-6 flex items-center justify-between">
        <NavLink to="/" className="text-2xl font-bold text-gray-800">TERO</NavLink>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <NavLink to="/" className="hover:text-gray-500">Home</NavLink>
            </li>
            <li>
              <NavLink to="/about" className="hover:text-gray-500">About</NavLink>
            </li>
            <li>
              <NavLink to="/products" className="hover:text-gray-500">Products</NavLink>
            </li>
          </ul>
        </nav>
        <div>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Find Now
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
