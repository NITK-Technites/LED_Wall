#include <gtkmm/application.h>
#include <gtkmm.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <iostream>
#include <fstream>
using namespace std;

#define GetCurrentDir getcwd

class TechnitesWindow : public Gtk::Window
{
	private:
		int i,j;
		std::string program_path,song_path;
	
	public:
		TechnitesWindow();
		virtual ~TechnitesWindow();

	protected:
	//Signal handlers:
	void on_button_program_clicked();
	void on_button_song_clicked();
	void button_run_clicked();

	//Child widgets:
	Gtk::ButtonBox m_ButtonBox;
	Gtk::Button button_program,button_song,button_run;
};

TechnitesWindow::TechnitesWindow() : m_ButtonBox(Gtk::ORIENTATION_VERTICAL),button_program("Select Program"),button_song("Select Song"),button_run("Run")
{
	i=j=0;
	set_title("App");

	add(m_ButtonBox);

	m_ButtonBox.pack_start(button_program);
	button_program.signal_clicked().connect(sigc::mem_fun(*this,&TechnitesWindow::on_button_program_clicked));

	m_ButtonBox.pack_start(button_song);
	button_song.signal_clicked().connect(sigc::mem_fun(*this,&TechnitesWindow::on_button_song_clicked));
              
	m_ButtonBox.pack_start(button_run);
	button_run.signal_clicked().connect(sigc::mem_fun(*this,&TechnitesWindow::button_run_clicked));

	show_all_children();
}

TechnitesWindow::~TechnitesWindow()
{
}

void TechnitesWindow::on_button_program_clicked()
{
	Gtk::FileChooserDialog dialog("Please choose a file",Gtk::FILE_CHOOSER_ACTION_OPEN);
	dialog.set_transient_for(*this);

	//Response Buttons
	dialog.add_button("_Cancel", Gtk::RESPONSE_CANCEL);
	dialog.add_button("_Open", Gtk::RESPONSE_OK);

	//Filters set
	Glib::RefPtr<Gtk::FileFilter> filter_py = Gtk::FileFilter::create();
	filter_py->set_name("Python files");
	filter_py->add_pattern("*.py");
	dialog.add_filter(filter_py);
  
	Glib::RefPtr<Gtk::FileFilter> filter_any = Gtk::FileFilter::create();
	filter_any->set_name("all files");
	filter_any->add_pattern("*");
	dialog.add_filter(filter_any);
  
	int result = dialog.run();

	//To handle the response:
	switch(result)
	{
		case(Gtk::RESPONSE_OK): program_path = dialog.get_filename();
					i++;
					std::cout << "File selected: " <<  program_path << std::endl;
					if(i==1 && j<=1)
					{
						ofstream myfile;
     				 		myfile.open("run.sh", ios::out);
  						if (myfile.is_open())
  						{
				    			myfile << "#!/bin/bash\n\nsudo python ";
							myfile << program_path << " " << song_path;
							myfile.close();
				  		}
				  		else 
				  			std::cout << "Unable to open file";
      					}	
      					else
      						std::cout << "Select Song\n";
      					break;
    
    		case(Gtk::RESPONSE_CANCEL): 	std::cout << "Cancel clicked." << std::endl;
						break;
    		default: std::cout << "Unexpected button clicked." << std::endl;
     			 break;    
  	}
}

void TechnitesWindow::on_button_song_clicked()
{
	Gtk::FileChooserDialog dialog("Please choose a file",Gtk::FILE_CHOOSER_ACTION_OPEN);
	dialog.set_transient_for(*this);

	//Response Buttons
	dialog.add_button("_Cancel", Gtk::RESPONSE_CANCEL);
	dialog.add_button("_Open", Gtk::RESPONSE_OK);

	//Filters set
	Glib::RefPtr<Gtk::FileFilter> filter_mp3 = Gtk::FileFilter::create();
	filter_mp3->set_name("MP3 files");
	filter_mp3->add_pattern("*.mp3");
	dialog.add_filter(filter_mp3);
 
	Glib::RefPtr<Gtk::FileFilter> filter_any = Gtk::FileFilter::create();
	filter_any->set_name("all files");
	filter_any->add_pattern("*");
	dialog.add_filter(filter_any);
 
	int result = dialog.run();

	//To handle the response:
	switch(result)
	{
		case(Gtk::RESPONSE_OK):	song_path = dialog.get_filename();
					j++;
					std::cout << "File selected: " <<  song_path << std::endl;
					if(i==0 || j==0)
						std::cout << "Select Program\n";
					else if(i==1 && j==1)
					{
						ofstream myfile;
						myfile.open("run.sh", ios::out);
						if (myfile.is_open())
						{
							myfile << "#!/bin/bash\n\nsudo python ";
							myfile << program_path << " " << song_path;
							myfile.close();
						}
						else
							std::cout << "Unable to open file";
      					}
      					else
      					{
      						ofstream myfile;
      						myfile.open("run.sh", ios::app);
      						if (myfile.is_open())
      						{
      							myfile << "\nsudo python " << program_path << " " << song_path;
      							myfile.close();
      						}
      						else
      							std::cout << "Unable to open file";
      					} 
      					break;
    
		case(Gtk::RESPONSE_CANCEL):	std::cout << "Cancel clicked." << std::endl;
      						break;
   		
   		default: std::cout << "Unexpected button clicked." << std::endl;
			 break;
	}
}


void TechnitesWindow::button_run_clicked()
{
	//To obtain current directory path
	char cCurrentPath[FILENAME_MAX];
	if(!GetCurrentDir(cCurrentPath,sizeof(cCurrentPath)))
		std::cout << " NO PATH ";	
		
	strcat(cCurrentPath,"/run.sh");
		
	//To run the shell script created (Shell script needs to be made executable the first time)
	system(cCurrentPath);
}


int main(int argc, char *argv[])
{
	Glib::RefPtr<Gtk::Application> app = Gtk::Application::create(argc, argv, "");

	TechnitesWindow window;
  
	window.set_default_size(180,300);
	window.set_title("Technites GUI");
	window.set_position(Gtk::WIN_POS_CENTER);
	window.set_border_width(10);

	//Shows the window and returns when it is closed.
	return app->run(window);
}
