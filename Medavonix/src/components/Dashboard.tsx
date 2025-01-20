import React from 'react';
import { useState } from 'react';
import { Clock, User, Search, AlignJustify} from 'lucide-react';

const Dashboard: React.FC = () => {

    const [slectedPatient, setSelected] = useState<boolean>(false);
    return (
        <div className='min-h-screen bg-gray-100'>
            <nav className ='bg-emerald-800 p-3'>
                <div className='flex justify-between items-center p-3'>
                    <div>
                        <h1 className='text-white text-3xl font-bold'>MedaVonix Dashboard</h1>
                    </div>

                    <div className='flex items-center space-x-4'>
                        <Clock className = 'text-white' size={30} />
                        <span className='text-white text-2xl'>
                            {new Date().toLocaleDateString()}
                        </span>
                        <User className='text-white' size={30}/>
                        <AlignJustify className='text-white' size={30}/>
                    </div>
                </div>
            </nav>

            <div className='flex'>
                Here we will have the details of the patient
            </div>

            
           
        </div>
    );
};

export default Dashboard;