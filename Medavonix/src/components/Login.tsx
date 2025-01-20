import React from 'react';
import {useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";

const Login: React.FC = () => {

    const navigate = useNavigate(); 

    const handleSubmit = (): void  => {
       
        navigate('/');
        
    };

  
    
    return (
<div className="flex flex-col items-center justify-center min-h-screen bg-emerald-800 text-white px-4">
  <h2 className="text-3xl font-bold mb-8">Login</h2>
  <form 
    onSubmit={handleSubmit} 
    className="bg-white text-black rounded-lg p-8 shadow-lg w-full max-w-md space-y-6"
  >
    <div className="space-y-2">
      <label htmlFor="username" className="block text-base font-medium text-gray-700" >
        Username:
      </label>
      <input 
        type="text" 
        id="username" 
        name="username" 
        placeholder="e.g. Manish"
        required 
        className="w-full h-10 border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
      />
    </div>
    <div className="space-y-2">
      <label htmlFor="password" className="block text-base font-medium text-gray-700">
        Password:
      </label>
      <input 
        type="password" 
        id="password" 
        name="password" 
        required 
        placeholder='e.g. @#$#MNH&78'
        className="w-full h-10 border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
      />
    </div>
    <div className="text-right">
      <p className="text-sm text-emerald-500 hover:underline cursor-pointer">
        Forgot Password?
      </p>
    </div>
    <button 
      type="submit" 
      onSubmit={handleSubmit} 
      className="w-full py-2 px-4 bg-emerald-500 text-white rounded-md hover:bg-emerald-600 font-semibold"
    >
      Login
    </button>
    <div className="text-center space-y-4">
      <p className="text-sm">Or Login With</p>
      <div className="flex justify-around space-x-4">
      <GoogleLogin
          onSuccess={(credentialResponse) => {
            try{
              const token  = credentialResponse.credential;
              if(!token){
                throw new Error('No token found');
              }
              const decode = jwtDecode(token);
              console.log('Decoded Toeken', decode);
              navigate('/');
            } catch (error){
              console.error('Error', error);
            }
          }}/>

        {/* <button 
          type="button" 
          onClick={handleSubmit}
          className="py-2 px-7 bg-blue-500 text-white rounded-md hover:bg-blue-600 font-semibold"
        >
          Google
        </button> */}

        {/* <button 
        
          type="button" 
          onClick={handleSubmit}
          className="py-2 px-4 bg-blue-800 text-white rounded-md hover:bg-blue-900 font-semibold w-[42%]"
        >
          Facebook
        </button> */}
      </div>
    </div>
  </form>
</div>

    );
};

export default Login;